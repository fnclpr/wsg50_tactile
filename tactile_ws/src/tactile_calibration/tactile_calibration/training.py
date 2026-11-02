"""Training pipeline: [zero samples] -> PCA -> MinMax -> tanh MLP -> wrench.

Faithfulness notes
------------------
Legacy (the_train.m): fitnet(90*ones(1,6)), tansig hidden / purelin output,
dividerand 50/40/10, trainscg, max_fail 150, 0.6 % zero samples added.
Those are the defaults here.

ENGINEERING DECISION: trainscg (scaled conjugate gradient) does not exist in
scikit-learn. We use Adam with mini-batches plus a legacy-style early stopping
(validation MSE, patience = max_fail, best weights restored). Results will
not be bit-identical to MATLAB; judge them with the validation metrics.

PCA and the input/target MinMax scalers are fitted on the full set passed in
(before the split), like MATLAB's train() does for its process functions.
"""
from __future__ import annotations

import datetime
import math
from dataclasses import asdict, dataclass
from typing import Callable, Optional

import numpy as np
import sklearn
from sklearn.neural_network import MLPRegressor

from .model import (TrainedModel, minmax_apply, regression_metrics,
                    safe_minmax)
from .pca_compression import fit_pca

N_TAXELS = 25
N_WRENCH = 6

# callback(epoch, train_mse, val_mse, best_val_mse) -> True to stop training
ProgressCallback = Callable[[int, float, float, float], Optional[bool]]


@dataclass
class TrainConfig:
    n_components: int = 15            # 0 = no PCA layer (legacy convention)
    hidden_layers: tuple = (90,) * 6
    split: tuple = (0.5, 0.4, 0.1)    # train / validation / test
    zero_fraction: float = 0.006      # legacy perc_zeros
    max_epochs: int = 1000
    max_fail: int = 150               # validation patience (legacy max_fail)
    batch_size: int = 256
    learning_rate: float = 1e-3
    l2: float = 0.0
    seed: int = 0

    def validate(self) -> None:
        if self.n_components < 0:
            raise ValueError("n_components must be >= 0")
        if any(int(h) < 1 for h in self.hidden_layers):
            raise ValueError("hidden layer sizes must be >= 1")
        if len(self.split) != 3 or any(s < 0 for s in self.split) \
                or not math.isclose(sum(self.split), 1.0, abs_tol=1e-6):
            raise ValueError("split must be 3 non-negative fractions summing to 1")
        if self.split[0] <= 0 or self.split[1] <= 0:
            raise ValueError("train and validation fractions must be > 0 (early stopping needs validation)")
        if not 0 <= self.zero_fraction < 1:
            raise ValueError("zero_fraction must be in [0, 1)")
        if self.max_epochs < 1 or self.max_fail < 1 or self.batch_size < 1:
            raise ValueError("max_epochs, max_fail and batch_size must be >= 1")
        if self.learning_rate <= 0 or self.l2 < 0:
            raise ValueError("learning_rate must be > 0 and l2 >= 0")


def split_indices(n: int, split: tuple, seed: int):
    """dividerand-like random split. Returns (train, val, test) index arrays."""
    perm = np.random.default_rng(seed).permutation(n)
    n_tr = max(1, int(round(split[0] * n)))
    n_va = max(1, int(round(split[1] * n)))
    if n_tr + n_va > n:
        n_va = n - n_tr
    if n_va < 1:
        raise ValueError("not enough samples to split")
    return perm[:n_tr], perm[n_tr:n_tr + n_va], perm[n_tr + n_va:]


def _mse(a, b) -> float:
    return float(np.mean((a - b) ** 2))


def train_model(voltages, wrench, config: Optional[TrainConfig] = None,
                broken_cells: tuple = (),
                callback: Optional[ProgressCallback] = None) -> TrainedModel:
    """Train on debiased voltages (N, 25) -> wrench (N, 6).

    broken_cells: 0-BASED taxel indices to ignore.
    """
    cfg = config or TrainConfig()
    cfg.validate()
    from . import __version__

    v = np.asarray(voltages, dtype=np.float64)
    y = np.asarray(wrench, dtype=np.float64)
    if v.ndim != 2 or v.shape[1] != N_TAXELS:
        raise ValueError(f"voltages must be (N, {N_TAXELS}), got {v.shape}")
    if y.shape != (v.shape[0], N_WRENCH):
        raise ValueError(f"wrench must be ({v.shape[0]}, {N_WRENCH}), got {y.shape}")
    if not (np.all(np.isfinite(v)) and np.all(np.isfinite(y))):
        raise ValueError("voltages/wrench contain NaN/inf")
    broken = tuple(sorted(set(int(c) for c in broken_cells)))
    if any(c < 0 or c >= N_TAXELS for c in broken):
        raise ValueError("broken_cells must be 0-based indices in [0, 24]")
    n_real = v.shape[0]
    if n_real < 20:
        raise ValueError("need at least 20 samples")

    # zero-wrench / zero-voltage samples (legacy perc_zeros)
    n_zero = int(math.ceil(cfg.zero_fraction * n_real))
    if n_zero:
        v = np.vstack([v, np.zeros((n_zero, N_TAXELS))])
        y = np.vstack([y, np.zeros((n_zero, N_WRENCH))])

    good = np.array([i for i in range(N_TAXELS) if i not in broken], dtype=int)

    # features
    pca = None
    if cfg.n_components > 0:
        pca = fit_pca(v, cfg.n_components, broken)
        z = pca.transform(v)
    else:
        z = v[:, good]
    in_min, in_max = safe_minmax(z)
    t_min, t_max = safe_minmax(y)
    zs = minmax_apply(z, in_min, in_max)
    ys = minmax_apply(y, t_min, t_max)

    tr, va, te = split_indices(v.shape[0], cfg.split, cfg.seed)

    mlp = MLPRegressor(hidden_layer_sizes=tuple(int(h) for h in cfg.hidden_layers),
                       activation="tanh", solver="adam", alpha=cfg.l2,
                       batch_size=min(cfg.batch_size, tr.size),
                       learning_rate_init=cfg.learning_rate, shuffle=True,
                       random_state=cfg.seed)

    best, fails, reason = math.inf, 0, "max_epochs"
    best_coefs = best_inter = None
    epochs_run = 0
    for epoch in range(1, cfg.max_epochs + 1):
        mlp.partial_fit(zs[tr], ys[tr])
        epochs_run = epoch
        tr_mse = _mse(mlp.predict(zs[tr]), ys[tr])
        va_mse = _mse(mlp.predict(zs[va]), ys[va])
        if va_mse < best:
            best, fails = va_mse, 0
            best_coefs = [c.copy() for c in mlp.coefs_]
            best_inter = [b.copy() for b in mlp.intercepts_]
        else:
            fails += 1
        if callback is not None and callback(epoch, tr_mse, va_mse, best):
            reason = "cancelled"
            break
        if fails >= cfg.max_fail:
            reason = "max_fail"
            break

    weights = [c.T.copy() for c in best_coefs]
    biases = [b.copy() for b in best_inter]
    activations = ["tanh"] * (len(weights) - 1) + ["linear"]

    # without PCA, re-insert broken taxels as zero columns (as gen_net_files.m does)
    if pca is None and broken:
        w0 = np.zeros((weights[0].shape[0], N_TAXELS))
        w0[:, good] = weights[0]
        weights[0] = w0
        full_min, full_max = -np.ones(N_TAXELS), np.ones(N_TAXELS)
        full_min[good], full_max[good] = in_min, in_max
        in_min, in_max = full_min, full_max

    model = TrainedModel(n_input=N_TAXELS, pca=pca, input_min=in_min, input_max=in_max,
                         weights=weights, biases=biases, activations=activations,
                         target_min=t_min, target_max=t_max, broken_cells=broken)

    # end-to-end metrics on raw voltages, wrench units
    metrics = {"train": regression_metrics(y[tr], model.predict(v[tr])),
               "validation": regression_metrics(y[va], model.predict(v[va]))}
    if te.size:
        metrics["test"] = regression_metrics(y[te], model.predict(v[te]))
    metrics["best_validation_mse_scaled"] = float(best)
    model.metrics = metrics
    model.metadata = {
        "package_version": __version__,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "config": {k: (list(v_) if isinstance(v_, tuple) else v_) for k, v_ in asdict(cfg).items()},
        "n_real_samples": n_real,
        "n_zero_samples_added": n_zero,
        "split_sizes": {"train": int(tr.size), "validation": int(va.size), "test": int(te.size)},
        "epochs_run": epochs_run,
        "stop_reason": reason,
        "numpy_version": np.__version__,
        "sklearn_version": sklearn.__version__,
        "optimizer": "adam (ENGINEERING DECISION: legacy used trainscg)",
    }
    return model

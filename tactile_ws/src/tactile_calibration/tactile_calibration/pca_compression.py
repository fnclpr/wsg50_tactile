"""PCA compression of the 25 tactile voltages.

Legacy equivalent (uclv_learning_lib_legacy/ANN_PCA_Layer.h):
    y = Ureduce.T @ (x - pca_mean)
No whitening, no scaling. n_components == 0 in the legacy code means
"no PCA layer"; here, simply do not call fit_pca.

Broken cells (legacy: finger_info.broken_cells, MATLAB 1-based) are removed
before fitting. In this module indices are 0-BASED (convert with c - 1 when
reading ProjectData/FingerInfo.broken_cells). The fitted model is expanded
back to n_input with zero rows in U and zeros in the mean, so the runtime
still takes all 25 voltages and broken cells contribute nothing
(same as gen_net_files.m).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import PCA


@dataclass(frozen=True)
class PcaModel:
    mean: NDArray[np.float64]                      # (n_input,)
    u_reduce: NDArray[np.float64]                  # (n_input, r), orthonormal columns
    explained_variance_ratio: NDArray[np.float64]  # (r,)
    broken_cells: tuple[int, ...]                  # 0-based

    @property
    def n_input(self) -> int:
        return int(self.mean.shape[0])

    @property
    def n_components(self) -> int:
        return int(self.u_reduce.shape[1])

    def transform(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        """x: (n_input,) or (N, n_input) -> (r,) or (N, r). y = U^T (x - mean)."""
        x = np.asarray(x, dtype=np.float64)
        if x.shape[-1] != self.n_input:
            raise ValueError(
                f"expected last dimension {self.n_input}, got {x.shape[-1]}")
        return (x - self.mean) @ self.u_reduce

    def inverse_transform(self, y: NDArray[np.float64]) -> NDArray[np.float64]:
        """Least-squares reconstruction; broken cells come back as 0."""
        y = np.asarray(y, dtype=np.float64)
        return y @ self.u_reduce.T + self.mean


def fit_pca(
    voltages: NDArray[np.float64],
    n_components: int,
    broken_cells: tuple[int, ...] = (),
) -> PcaModel:
    """Fit PCA on (N, n_input) debiased voltages.

    n_components must be in [1, n_input - len(broken_cells)].
    """
    v = np.asarray(voltages, dtype=np.float64)
    if v.ndim != 2:
        raise ValueError("voltages must be 2-D (N, n_input)")
    if not np.all(np.isfinite(v)):
        raise ValueError("voltages contain NaN/inf")
    n_in = v.shape[1]
    broken = tuple(sorted(set(int(c) for c in broken_cells)))
    if any(c < 0 or c >= n_in for c in broken):
        raise ValueError(f"broken_cells out of range [0, {n_in - 1}]: {broken}")

    good = np.array([i for i in range(n_in) if i not in broken], dtype=int)
    if not 1 <= n_components <= good.size:
        raise ValueError(f"n_components must be in [1, {good.size}]")
    if v.shape[0] < n_components + 1:
        raise ValueError("not enough samples for the requested components")

    pca = PCA(n_components=n_components, svd_solver="full", whiten=False)
    pca.fit(v[:, good])

    u_full = np.zeros((n_in, n_components))
    u_full[good, :] = pca.components_.T
    mean_full = np.zeros(n_in)
    mean_full[good] = pca.mean_

    return PcaModel(
        mean=mean_full,
        u_reduce=u_full,
        explained_variance_ratio=pca.explained_variance_ratio_.copy(),
        broken_cells=broken,
    )

"""Trained calibration model: PCA -> MinMax(in) -> FC layers -> MinMax(reverse).

Mirrors the legacy layer chain of uclv_learning_lib_legacy (see
gen_net_files.m / ANN_File_Reader.cpp):

    [PCA]  y = U^T (x - mean)                      layer code 1
    MapMinMax        2 (x - min)/(max - min) - 1   layer code 2
    FullyConnected   act(W x + b), tansig/purelin  layer code 4
    MapMinMax(rev)   (max - min)/2 (y + 1) + min   layer code 3

tansig(x) = 2/(1+exp(-2x)) - 1 == tanh(x) exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from .pca_compression import PcaModel

WRENCH_NAMES = ("fx", "fy", "fz", "taux", "tauy", "tauz")
ACTIVATIONS = {"tanh": np.tanh, "linear": lambda x: x}
MIN_RANGE = 1e-12


def safe_minmax(data: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Column-wise (min, max). A (near-)constant column gets (c-1, c+1)
    so the mapping stays finite (legacy sets removed inputs to (-1, 1))."""
    lo = data.min(axis=0).astype(np.float64)
    hi = data.max(axis=0).astype(np.float64)
    degenerate = (hi - lo) < MIN_RANGE
    lo = np.where(degenerate, lo - 1.0, lo)
    hi = np.where(degenerate, hi + 1.0, hi)
    return lo, hi


def minmax_apply(x, lo, hi):
    return 2.0 * (x - lo) / (hi - lo) - 1.0


def minmax_reverse(y, lo, hi):
    return (hi - lo) / 2.0 * (y + 1.0) + lo


def regression_metrics(y_true: NDArray, y_pred: NDArray) -> dict:
    """Per-component RMSE, MAE, max |error|, R^2 (NaN if a component is constant)."""
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    err = y_pred - y_true
    ss_res = np.sum(err**2, axis=0)
    ss_tot = np.sum((y_true - y_true.mean(axis=0)) ** 2, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        r2 = np.where(ss_tot > 0, 1.0 - ss_res / ss_tot, np.nan)
    return {
        "n_samples": int(y_true.shape[0]),
        "components": list(WRENCH_NAMES[: y_true.shape[1]]),
        "rmse": [float(v) for v in np.sqrt(np.mean(err**2, axis=0))],
        "mae": [float(v) for v in np.mean(np.abs(err), axis=0)],
        "max_abs_error": [float(v) for v in np.max(np.abs(err), axis=0)],
        "r2": [float(v) for v in r2],
    }


@dataclass
class TrainedModel:
    n_input: int
    pca: Optional[PcaModel]
    input_min: NDArray[np.float64]
    input_max: NDArray[np.float64]
    weights: list            # each (n_out, n_in)
    biases: list             # each (n_out,)
    activations: list        # "tanh" | "linear"
    target_min: NDArray[np.float64]
    target_max: NDArray[np.float64]
    broken_cells: tuple = ()  # 0-based
    metrics: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        first_in = self.pca.n_components if self.pca is not None else self.n_input
        if self.pca is not None and self.pca.n_input != self.n_input:
            raise ValueError("PCA input size does not match n_input")
        if not (len(self.weights) == len(self.biases) == len(self.activations) >= 1):
            raise ValueError("weights/biases/activations length mismatch")
        if self.input_min.shape != (first_in,) or self.input_max.shape != (first_in,):
            raise ValueError("input min/max size does not match first layer input")
        prev = first_in
        for i, (w, b, a) in enumerate(zip(self.weights, self.biases, self.activations)):
            if a not in ACTIVATIONS:
                raise ValueError(f"unknown activation '{a}'")
            if w.ndim != 2 or w.shape[1] != prev or b.shape != (w.shape[0],):
                raise ValueError(f"layer {i}: inconsistent shapes {w.shape}, {b.shape}, prev={prev}")
            prev = w.shape[0]
        if self.activations[-1] != "linear":
            raise ValueError("output layer must be linear (legacy purelin)")
        if self.target_min.shape != (prev,) or self.target_max.shape != (prev,):
            raise ValueError("target min/max size does not match output size")
        if np.any(self.input_max - self.input_min <= 0) or np.any(self.target_max - self.target_min <= 0):
            raise ValueError("min/max ranges must be positive")

    @property
    def n_output(self) -> int:
        return int(self.weights[-1].shape[0])

    def predict(self, x) -> NDArray[np.float64]:
        """x: (n_input,) or (N, n_input) debiased voltages -> wrench (n_output,) or (N, n_output)."""
        x = np.asarray(x, dtype=np.float64)
        single = x.ndim == 1
        z = np.atleast_2d(x)
        if z.shape[1] != self.n_input:
            raise ValueError(f"expected {self.n_input} inputs, got {z.shape[1]}")
        if self.pca is not None:
            z = self.pca.transform(z)
        z = minmax_apply(z, self.input_min, self.input_max)
        for w, b, a in zip(self.weights, self.biases, self.activations):
            z = ACTIVATIONS[a](z @ w.T + b)
        y = minmax_reverse(z, self.target_min, self.target_max)
        return y[0] if single else y

    def evaluate(self, voltages, wrench) -> dict:
        return regression_metrics(wrench, self.predict(voltages))

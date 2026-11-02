"""Load training arrays from a ProjectData session or a plain .npz file.

.npz layout (e.g. exported from MATLAB/numpy):
    voltages      (N, 25)  debiased voltages
    wrench        (N, 6)   [fx fy fz taux tauy tauz]
    broken_cells  (optional) 1-BASED taxel numbers, same as ProjectData
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import numpy as np


def load_arrays(path: Union[str, Path], decimation_radius: float = 0.0,
                broken_cells_1based: Optional[tuple] = None):
    """Returns (voltages, wrench, broken_cells_0based, info)."""
    path = Path(path)
    info = {"source": str(path)}
    if path.suffix.lower() == ".npz":
        with np.load(path) as f:
            v, y = f["voltages"], f["wrench"]
            stored = tuple(int(c) for c in f["broken_cells"]) if "broken_cells" in f.files else ()
        if decimation_radius > 0:
            raise ValueError("decimation is only available for ProjectData sessions")
    else:
        try:
            from tactile_core.calibration.dataset import ProjectData
            from tactile_core.calibration.decimation import decimate_project_data
        except ImportError as e:  # pragma: no cover
            raise ImportError("tactile_core is required to load ProjectData sessions "
                              "(pip install -e src/tactile_core)") from e
        pd = ProjectData.load(path)
        info["finger_id"] = pd.finger_info.finger_id
        info["n_samples_before_decimation"] = pd.num_samples()
        if decimation_radius > 0:
            pd = decimate_project_data(pd, decimation_radius)
            info["decimation_radius"] = decimation_radius
        v, y = pd.voltages_rect, pd.wrench
        stored = tuple(int(c) for c in pd.finger_info.broken_cells)
    broken1 = stored if broken_cells_1based is None else tuple(broken_cells_1based)
    if any(c < 1 or c > 25 for c in broken1):
        raise ValueError("broken cells are 1-based taxel numbers in [1, 25]")
    info["broken_cells_1based"] = list(broken1)
    return (np.asarray(v, dtype=np.float64), np.asarray(y, dtype=np.float64),
            tuple(c - 1 for c in broken1), info)

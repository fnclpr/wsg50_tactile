"""
Direct port of:
    matlab_calibration_gui/gui_lib/compute_centroid.m

Implements Eq. (3)-(4) of Costanzo et al., Sensors 2019, 19, 966:

    xC = sum_i(xi * dvi) / sum_i(dvi)
    yC = sum_i(yi * dvi) / sum_i(dvi)

where dvi is the (already debiased) voltage of taxel i and (xi, yi) are
its physical coordinates on the 5x5 grid.

MATLAB reference (verbatim):

    function centroid = compute_centroid(voltages, taxels_x_coords, taxels_y_coords, broken_cells)
    if nargin > 3
        voltages(broken_cells) = 0;
    end
    sumV = sum(voltages(:));
    if any( abs(voltages) > 0.01 )
        voltages_matrix = reshape(voltages,5,5)';
        x = sum(sum(voltages_matrix.*taxels_x_coords))/sumV;
        y = sum(sum(voltages_matrix.*taxels_y_coords))/sumV;
    else
        x = 0;
        y = 0;
    end
    centroid = [x;y];

Numpy note: MATLAB's `reshape(v,5,5)'` (column-major reshape then
transpose) on a length-25 vector `v` is exactly equivalent to numpy's
default (row-major / C-order) `v.reshape(5, 5)`. This has been verified
algebraically (see project analysis doc, Section B) and is exercised by
test_centroid.py.
"""
from __future__ import annotations

import numpy as np

VOLTAGE_ACTIVITY_THRESHOLD = 0.01  # matches the literal 0.01 in the MATLAB source


def compute_centroid(
    voltages: np.ndarray,
    taxels_x_coords: np.ndarray,
    taxels_y_coords: np.ndarray,
    broken_cells: "list[int] | np.ndarray | None" = None,
) -> np.ndarray:
    """Compute the weighted centroid of the tactile map.

    Parameters
    ----------
    voltages:
        Length-25 array of (already debiased) taxel voltages, in the
        same 1D ordering used by the sensor driver (taxel index 0..24,
        row-major over the 5x5 grid — see PAPER AMBIGUITY 3 in the
        project analysis doc; must be verified against firmware).
    taxels_x_coords, taxels_y_coords:
        5x5 arrays of physical taxel coordinates in meters, matching
        `finger_info.taxels_x_coords` / `taxels_y_coords` from
        `struct_finger_info.m`.
    broken_cells:
        Optional 1-INDEXED (MATLAB-convention) list of taxel numbers to
        zero out before computing the centroid, matching
        `finger_info.broken_cells`. Pass None (default) if there are no
        known-bad taxels.

    Returns
    -------
    np.ndarray, shape (2,)
        [x, y] centroid coordinates in meters. Returns [0, 0] if no
        taxel exceeds the activity threshold (i.e. no contact detected).
    """
    voltages = np.asarray(voltages, dtype=float).reshape(-1).copy()
    if voltages.size != 25:
        raise ValueError(f"voltages must have 25 elements, got {voltages.size}")

    if broken_cells is not None:
        broken_cells = np.asarray(broken_cells, dtype=int)
        # MATLAB is 1-indexed; convert to 0-indexed for numpy.
        voltages[broken_cells - 1] = 0.0

    sum_v = float(np.sum(voltages))

    if np.any(np.abs(voltages) > VOLTAGE_ACTIVITY_THRESHOLD):
        voltages_matrix = voltages.reshape(5, 5)  # see module docstring re: MATLAB equivalence
        x = float(np.sum(voltages_matrix * taxels_x_coords) / sum_v)
        y = float(np.sum(voltages_matrix * taxels_y_coords) / sum_v)
    else:
        x = 0.0
        y = 0.0

    return np.array([x, y])

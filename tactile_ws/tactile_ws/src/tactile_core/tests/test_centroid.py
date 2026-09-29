"""
Reference values in this file are hand-derived from the MATLAB source
(compute_centroid.m), not from running the Python implementation.
See the module docstring in tactile_core/processing/centroid.py for
the exact taxel-coordinate convention used here, matching
struct_finger_info.m's defaults:

    taxels_x_coords[row, col] = 0.007 * [-1, -0.5, 0, 0.5, 1][col]
    taxels_y_coords[row, col] = 0.007 * [ 1,  0.5, 0,-0.5,-1][row]

and the 1D voltage vector is indexed row-major: voltages[row*5+col].
"""
import numpy as np
import pytest

from tactile_core.processing.centroid import compute_centroid

X_ROW = np.array([-1.0, -0.5, 0.0, 0.5, 1.0]) * 0.007
Y_COL = np.array([1.0, 0.5, 0.0, -0.5, -1.0]) * 0.007

TAXELS_X = np.tile(X_ROW, (5, 1))          # constant across rows, varies across columns
TAXELS_Y = np.tile(Y_COL.reshape(5, 1), (1, 5))  # constant across columns, varies across rows


def test_zero_input_gives_zero_centroid():
    voltages = np.zeros(25)
    result = compute_centroid(voltages, TAXELS_X, TAXELS_Y)
    np.testing.assert_allclose(result, [0.0, 0.0])


def test_below_activity_threshold_gives_zero_centroid():
    # 0.005 < VOLTAGE_ACTIVITY_THRESHOLD (0.01) -> "no contact" branch
    voltages = np.full(25, 0.005)
    result = compute_centroid(voltages, TAXELS_X, TAXELS_Y)
    np.testing.assert_allclose(result, [0.0, 0.0])


def test_single_active_taxel_top_right():
    # taxel (row=0, col=4) -> 1D index 4 -> physical coords (x=+0.007, y=+0.007)
    voltages = np.zeros(25)
    voltages[4] = 2.0
    result = compute_centroid(voltages, TAXELS_X, TAXELS_Y)
    np.testing.assert_allclose(result, [0.007, 0.007])


def test_two_active_taxels_symmetric():
    # taxel index 4  -> (row0,col4) -> (+0.007, +0.007), weight 1.0
    # taxel index 20 -> (row4,col0) -> (-0.007, -0.007), weight 3.0
    voltages = np.zeros(25)
    voltages[4] = 1.0
    voltages[20] = 3.0
    result = compute_centroid(voltages, TAXELS_X, TAXELS_Y)
    # hand-derived: sumV=4.0
    # x = (1*0.007 + 3*(-0.007)) / 4 = -0.014/4 = -0.0035
    # y = same by symmetry = -0.0035
    np.testing.assert_allclose(result, [-0.0035, -0.0035])


def test_broken_cell_is_zeroed_before_threshold_check():
    # Only taxel #5 (1-indexed) == index 4 (0-indexed) is active; marking
    # it broken must zero it out BEFORE the activity threshold is
    # checked, so the function must fall back to the [0,0] branch
    # rather than dividing by zero.
    voltages = np.zeros(25)
    voltages[4] = 2.0
    result = compute_centroid(voltages, TAXELS_X, TAXELS_Y, broken_cells=[5])
    np.testing.assert_allclose(result, [0.0, 0.0])


def test_wrong_length_raises():
    with pytest.raises(ValueError):
        compute_centroid(np.zeros(24), TAXELS_X, TAXELS_Y)

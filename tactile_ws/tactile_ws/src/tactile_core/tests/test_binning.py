"""
Reference values hand-derived the same way as test_zoning.py's
find_interval tests, since compute_fn_index is a thin wrapper around
find_interval + the -1 sentinel conversion.
"""
from tactile_core.calibration.binning import compute_fn_index

FN_INTERVALS = [0.0, 2.0, 4.0, 6.0, 8.5]  # matches struct_calib_data.m default


def test_compute_fn_index_middle_bin():
    assert compute_fn_index(3.0, FN_INTERVALS) == 2


def test_compute_fn_index_applies_abs():
    # matches the legacy call site: find_interval(..., abs(wrench(3)))
    assert compute_fn_index(-3.0, FN_INTERVALS) == compute_fn_index(3.0, FN_INTERVALS)


def test_compute_fn_index_left_edge():
    assert compute_fn_index(0.0, FN_INTERVALS) == 1


def test_compute_fn_index_right_edge():
    assert compute_fn_index(8.5, FN_INTERVALS) == 4
    assert compute_fn_index(-8.5, FN_INTERVALS) == 4


def test_compute_fn_index_out_of_range_is_sentinel():
    assert compute_fn_index(100.0, FN_INTERVALS) == -1
    assert compute_fn_index(-100.0, FN_INTERVALS) == -1

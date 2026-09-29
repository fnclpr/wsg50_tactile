"""
Reference values hand-derived from:
    find_interval.m
    find_geometric_zone.m
    compute_num_zones.m

NOTE: indices returned are 1-INDEXED (MATLAB convention), by design —
see the module docstring in tactile_core/processing/zoning.py.
"""
import math

import numpy as np

from tactile_core.processing.zoning import (
    compute_num_zones,
    find_geometric_zone,
    find_interval,
)

FN_INTERVALS = [0.0, 2.0, 4.0, 6.0, 8.5]  # matches struct_calib_data.m default


def test_find_interval_middle_bin():
    # value=3 in [0,2,4,6,8.5]: first breakpoint >= 3 is 4 (1-indexed pos 3), minus 1 = 2
    assert find_interval(FN_INTERVALS, 3.0) == 2.0


def test_find_interval_left_edge_special_case():
    assert find_interval(FN_INTERVALS, 0.0) == 1.0


def test_find_interval_right_edge():
    # value == interval[-1] exactly -> last bin
    assert find_interval(FN_INTERVALS, 8.5) == 4.0


def test_find_interval_out_of_range_is_nan():
    assert math.isnan(find_interval(FN_INTERVALS, 9.0))
    assert math.isnan(find_interval(FN_INTERVALS, -1.0))


def test_compute_num_zones_default_config():
    # matches create_empty_project.m defaults: 4 angle bound lines, 3 radius intervals
    angle_bound_lines = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]
    radius_intervals = [0.0015, 0.0045, 0.01]
    assert compute_num_zones(angle_bound_lines, radius_intervals) == 9


def test_find_geometric_zone_center_is_zone_1():
    assert find_geometric_zone([0.0, 0.0], _angle_bound_lines(), _radius_intervals()) == 1.0


def test_find_geometric_zone_offaxis_theta_zero():
    # rho=0.007 (bin 3 of [-1,0.0015,0.0045,0.01]), theta=0 (bin: NaN -> forced to 1)
    # hand-derived: zone_index = (3-2)*4 + 1 + 1 = 6
    result = find_geometric_zone([0.007, 0.0], _angle_bound_lines(), _radius_intervals())
    assert result == 6.0


def test_find_geometric_zone_offaxis_theta_pi():
    # rho=0.007 (bin 3), theta=pi -> find_interval(angle_bound_lines, pi) = 2, theta_index = 3
    # hand-derived: zone_index = (3-2)*4 + 3 + 1 = 8
    result = find_geometric_zone([-0.007, 0.0], _angle_bound_lines(), _radius_intervals())
    assert result == 8.0


def test_find_geometric_zone_outside_sensor_is_nan():
    result = find_geometric_zone([1.0, 1.0], _angle_bound_lines(), _radius_intervals())
    assert math.isnan(result)


def _angle_bound_lines():
    return [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]


def _radius_intervals():
    return [0.0015, 0.0045, 0.01]

"""
Direct port of:
    matlab_calibration_gui/gui_lib/find_interval.m
    matlab_calibration_gui/gui_lib/find_geometric_zone.m
    matlab_calibration_gui/gui_lib/compute_num_zones.m

These implement the "stratification" of the calibration input space
into (polar-area x normal-force-interval) bins described in Section
3.1 (last paragraph) of Costanzo et al., Sensors 2019, 19, 966.

IMPORTANT — indexing convention: this module deliberately preserves
MATLAB's 1-INDEXED return values (interval/zone index 1 = first bin,
NaN = out of range) rather than converting to 0-indexed Python
convention. This is intentional for Step 1: it lets us validate
numerically against the legacy MATLAB behavior and against the
existing dataset structures (`struct_calib_data.m` cell arrays are
1-indexed by these same functions). A 0-indexed convenience wrapper
will be added when this is integrated into the ROS2 processing nodes
in a later step — do not silently renumber before that wrapper exists,
or downstream code that still expects 1-indexed values will break.

MATLAB reference (find_interval.m, verbatim):

    function interval_index = find_interval(interval,value)
    % Find the interval index of value inside interval
        if value > interval(1) && value <= interval(end)
            interval_index = find(value <= interval, 1) - 1;
        elseif value == interval(1)
            interval_index = 1;
        else
            interval_index = nan;
        end

MATLAB reference (compute_num_zones.m, verbatim):

    function num_zones = compute_num_zones(zone_angle_bound_lines,zone_radius_intervals)
    num_zones = 1+length(zone_angle_bound_lines)*(length(zone_radius_intervals)-1);
    end

MATLAB reference (find_geometric_zone.m, verbatim):

    function zone_index = find_geometric_zone(centroid,angle_bound_lines, zone_radius_intervals)
    [theta,rho] = cart2pol(centroid(1),centroid(2));
    theta = wrapTo2Pi(theta);
    rho_index = find_interval([-1 zone_radius_intervals],rho);
    if isnan(rho_index)
        zone_index = nan;
        return;
    elseif rho_index == 1
        zone_index = 1;
        return;
    end
    theta_index = find_interval(angle_bound_lines,theta)+1;
    if isnan(theta_index)
        theta_index = 1;
    end
    zone_index = (rho_index-2)*length(angle_bound_lines)+theta_index+1;
"""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np

NAN = float("nan")


def find_interval(interval: Sequence[float], value: float) -> float:
    """Find the 1-indexed bin of `value` inside the strictly increasing
    breakpoints `interval`.

    Bin i (1-indexed, i in [1, len(interval)-1]) covers
    (interval[i-1], interval[i]]. Returns 1 if value == interval[0]
    exactly (left-edge special case, matching MATLAB). Returns NaN if
    value is outside [interval[0], interval[-1]].
    """
    interval = np.asarray(interval, dtype=float)

    if interval[0] < value <= interval[-1]:
        # MATLAB: find(value <= interval, 1) - 1   (1-indexed find, minus 1)
        first_ge_1indexed = int(np.argmax(value <= interval)) + 1
        return float(first_ge_1indexed - 1)
    elif value == interval[0]:
        return 1.0
    else:
        return NAN


def compute_num_zones(zone_angle_bound_lines: Sequence[float], zone_radius_intervals: Sequence[float]) -> int:
    """Total number of geometric zones: 1 central zone + (radius bins) x (angle bins)."""
    return 1 + len(zone_angle_bound_lines) * (len(zone_radius_intervals) - 1)


def _wrap_to_2pi(theta: float) -> float:
    """Port of MATLAB's wrapTo2Pi: maps an angle to [0, 2*pi)."""
    two_pi = 2.0 * math.pi
    wrapped = theta % two_pi
    return wrapped


def find_geometric_zone(
    centroid: Sequence[float],
    angle_bound_lines: Sequence[float],
    zone_radius_intervals: Sequence[float],
) -> float:
    """Map a 2D centroid to its 1-indexed geometric zone number.

    Zone 1 is always the central zone (rho within the first radius
    bin, i.e. inside `zone_radius_intervals[0]`). Zones 2..N are the
    (radius-bin x angle-bin) combinations, radius-major.

    Returns NaN if the centroid falls outside the outermost radius
    (i.e. outside the sensor's calibrated area).
    """
    cx, cy = float(centroid[0]), float(centroid[1])
    rho = math.hypot(cx, cy)
    theta = _wrap_to_2pi(math.atan2(cy, cx))

    extended_radius_breakpoints = [-1.0] + list(zone_radius_intervals)
    rho_index = find_interval(extended_radius_breakpoints, rho)

    if math.isnan(rho_index):
        return NAN
    if rho_index == 1:
        return 1.0

    theta_index = find_interval(angle_bound_lines, theta) + 1
    if math.isnan(theta_index):
        theta_index = 1.0

    zone_index = (rho_index - 2) * len(angle_bound_lines) + theta_index + 1
    return zone_index

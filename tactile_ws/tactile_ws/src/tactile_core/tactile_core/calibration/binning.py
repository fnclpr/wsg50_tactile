"""
Small glue helper for mapping a measured normal force (fz) to its
1-indexed fn bin, using the SAME -1 = "invalid/out of range" sentinel
convention as ProjectData.zone_index and tactile_msgs/TactileProcessed
(Step 6/8).

Kept separate from tactile_core.processing.zoning.find_interval
because that module deliberately preserves MATLAB's 1-indexed/NaN
convention verbatim (see its module docstring) for direct validation
against the legacy code. This module is the ROS2/GUI-facing
translation layer on top of it -- the only place that NaN gets turned
into the -1 sentinel actually used in message fields and dataset
columns.

Traces to the legacy line in robot_calibration_gui's
F_receiveCalibData:
    fn_index = find_interval(app.projectData.calib_data.fn_intervals, abs(wrench(3)));
"""
from __future__ import annotations

import math
from typing import Sequence

from tactile_core.processing.zoning import find_interval


def compute_fn_index(fz: float, fn_intervals: Sequence[float]) -> int:
    """Map a normal force to its 1-indexed fn bin, or -1 if fz's
    magnitude falls outside the configured fn_intervals."""
    fn = find_interval(list(fn_intervals), abs(fz))
    return -1 if math.isnan(fn) else int(fn)

"""
Direct port of:
    matlab_calibration_gui/gui_lib/transform_wrench.m

Implements Eq. (8)-(9) of Costanzo et al., Sensors 2019, 19, 966:

    f^t = R^t_s * f^s
    tau^t = R^t_s * tau^s + p^t_s x f^t

MATLAB reference (verbatim):

    function t_wrench = transform_wrench(t_T_s, s_wrench )
    % transform a wrench, t=target frame, s=source frame
    t_wrench = zeros(6,1);
    t_wrench(1:3) = t_T_s(1:3,1:3) * s_wrench(1:3);
    t_wrench(4:6) = t_T_s(1:3,1:3) * s_wrench(4:6) + cross(t_T_s(1:3,4) ,t_wrench(1:3));
"""
from __future__ import annotations

import numpy as np


def transform_wrench(t_transform_s: np.ndarray, s_wrench: np.ndarray) -> np.ndarray:
    """Transform a 6D wrench [f; tau] from source frame s to target frame t.

    Parameters
    ----------
    t_transform_s: (4,4) homogeneous transform of frame s w.r.t. frame t.
    s_wrench: (6,) array [fx, fy, fz, taux, tauy, tauz] expressed in frame s.

    Returns
    -------
    np.ndarray, shape (6,): the wrench expressed in frame t.
    """
    s_wrench = np.asarray(s_wrench, dtype=float).reshape(6)
    r = t_transform_s[:3, :3]
    p = t_transform_s[:3, 3]

    f_t = r @ s_wrench[:3]
    tau_t = r @ s_wrench[3:6] + np.cross(p, f_t)

    return np.concatenate([f_t, tau_t])

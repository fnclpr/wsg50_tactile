"""
Direct port of:
    matlab_calibration_gui/gui_lib/compute_max_ft.m
    matlab_calibration_gui/gui_lib/compute_max_taun.m
    matlab_calibration_gui/gui_lib/compute_wrench_plot_point.m

Implements Eq. (1)-(2) of Costanzo et al., Sensors 2019, 19, 966:

    ftmax  = mu * fn
    taunmax = alpha * fn^(gamma+1)

mu, alpha, gamma are NOT derivable from this paper; the paper states
they are "experimentally estimated through the procedure described
in [16]" (a separate publication). They must be measured per-sensor
and stored as calibration metadata — never hardcoded as a global
constant. See PAPER AMBIGUITY 2 in the project analysis document.

MATLAB reference (verbatim):

    function maxFt = compute_max_ft(fn,mu)
    maxFt = mu*abs(fn);

    function maxM = compute_max_taun(fn, alpha, gamma)
    maxM = alpha*(abs(fn)^(gamma+1));

    function wrench_plot_point = compute_wrench_plot_point(wrench,fz_nominal,transform_of_central_zone, param_mu, param_alpha, param_gamma)
    wrench_transformed = transform_wrench(transform_of_central_zone,wrench);
    contact_fn_nominal = transform_of_central_zone(3,3)*fz_nominal; %transform the vector [0;0;fz]
    max_ft_nominal = compute_max_ft(contact_fn_nominal, param_mu);
    max_taun_nominal = compute_max_taun(contact_fn_nominal, param_alpha, param_gamma);
    wrench_plot_point = [wrench_transformed(1:2)/max_ft_nominal; wrench_transformed(end)/max_taun_nominal];
"""
from __future__ import annotations

import numpy as np

from .wrench_transform import transform_wrench


def compute_max_ft(fn: float, mu: float) -> float:
    """Eq. (1): maximum tangential force before slippage, ftmax = mu * |fn|."""
    return mu * abs(fn)


def compute_max_taun(fn: float, alpha: float, gamma: float) -> float:
    """Eq. (2): maximum torsional moment before slippage, taunmax = alpha * |fn|^(gamma+1)."""
    return alpha * (abs(fn) ** (gamma + 1))


def compute_wrench_plot_point(
    wrench: np.ndarray,
    fz_nominal: float,
    transform_of_central_zone: np.ndarray,
    param_mu: float,
    param_alpha: float,
    param_gamma: float,
) -> np.ndarray:
    """Normalize a 6D wrench sample into the 3D [ft_x*, ft_y*, taun*]
    limit-surface plot point used by the calibration GUI's unit-sphere
    visualization.

    Parameters
    ----------
    wrench: (6,) array [fx, fy, fz, taux, tauy, tauz] in the sensor frame.
    fz_nominal: nominal normal force for this fn-interval (bin center).
    transform_of_central_zone: (4,4) cont_T_sc for the sample's zone,
        as produced by `compute_zone_central_transforms`.
    param_mu, param_alpha, param_gamma: limit-surface constants (see
        module docstring — per-sensor, not universal).

    Returns
    -------
    np.ndarray, shape (3,): [ft_x / ftmax, ft_y / ftmax, taun / taunmax]
    """
    wrench_transformed = transform_wrench(transform_of_central_zone, wrench)

    # transform_of_central_zone(3,3) in MATLAB (1-indexed) is the (2,2)
    # element in 0-indexed numpy -- the z-component scaling of a pure
    # [0;0;fz] vector rotated into the contact frame.
    contact_fn_nominal = transform_of_central_zone[2, 2] * fz_nominal

    max_ft_nominal = compute_max_ft(contact_fn_nominal, param_mu)
    max_taun_nominal = compute_max_taun(contact_fn_nominal, param_alpha, param_gamma)

    return np.array(
        [
            wrench_transformed[0] / max_ft_nominal,
            wrench_transformed[1] / max_ft_nominal,
            wrench_transformed[5] / max_taun_nominal,  # wrench_transformed(end) == tauz
        ]
    )

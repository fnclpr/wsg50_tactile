"""
Direct port of:
    matlab_calibration_gui/gui_lib/compute_contact_transform.m
    matlab_calibration_gui/gui_lib/compute_zone_central_transforms.m

Implements Eq. (5)-(7) of Costanzo et al., Sensors 2019, 19, 966:
projecting a 2D centroid onto the undeformed silicone sphere and
building the homogeneous transform of the calibration-sensor frame
(Sigma_sens/Sigma_sc in the code) with respect to the contact frame
(Sigma_CoP/Sigma_cont in the code).

Frame naming (kept identical to the MATLAB variable names for
traceability):
    sf   = Sigma_sph : frame at the center of the undeformed sphere
    sc   = Sigma_sens/calib-sensor frame (what the code calls "sc")
    cont = Sigma_CoP : contact frame

MATLAB reference (compute_contact_transform.m, verbatim):

    function  cont_T_sc = compute_contact_transform(centroid, silicon_sphere_radius, z_coord_sphere_frame_wrt_calib_sensor_frame)
        sf_P_cont = [ centroid(1) ; centroid(2); sqrt( (silicon_sphere_radius^2) - (centroid(1)^2) - (centroid(2)^2) ) ];
        n_hat = sf_P_cont/silicon_sphere_radius;
        sc_x_cont = [1;0;0] - n_hat(1)*n_hat;
        sc_x_cont = sc_x_cont/norm(sc_x_cont);
        sc_y_cont = [0;1;0] - n_hat(2)*n_hat;
        sc_y_cont = sc_y_cont/norm(sc_y_cont);
        sc_R_cont = [ sc_x_cont , sc_y_cont , n_hat];
        sc_T_sf = [ eye(3) , [0 ; 0 ; z_coord_sphere_frame_wrt_calib_sensor_frame] ; [0 0 0 1] ];
        sc_P_cont_tilde = sc_T_sf * [sf_P_cont ; 1];
        sc_T_cont = [ [ sc_R_cont ; [0 0 0] ] ,  sc_P_cont_tilde ];
        cont_T_sc = inv(sc_T_cont);
    end

IMPORTANT — non-orthonormal rotation approximation (found while writing
Step 1's tests, not visible from reading the MATLAB in isolation):
`sc_x_cont` and `sc_y_cont` are each individually projected onto the
tangent plane and normalized, but they are NOT re-orthogonalized
against each other (no Gram-Schmidt/cross-product step). Each is
guaranteed unit-norm and exactly orthogonal to `n_hat`, but
`sc_x_cont . sc_y_cont` is only approximately zero, and the
approximation degrades as the centroid offset (cx, cy) grows relative
to the sphere radius R. This is a property of the ORIGINAL algorithm
(present identically in the MATLAB source), not a porting bug — do not
"fix" it by orthogonalizing, or the Python and MATLAB outputs will
diverge. It is presumably acceptable because real contact-patch
centroids stay small relative to R. Treat this as an ENGINEERING
ASSUMPTION carried over from the legacy code; flag for the domain
expert (paper authors) if sub-degree accuracy at large offsets ever
matters.

MATLAB reference (compute_zone_central_transforms.m, verbatim):

    function [ trasform_cell ] = compute_zone_central_transforms( zone_radius_centers , silicon_sphere_radius, z_coord_sphere_frame_wrt_calib_sensor_frame,zone_angle_center_lines )
    trasform_cell{1} = ([eye(3) , [0;0; -(silicon_sphere_radius+z_coord_sphere_frame_wrt_calib_sensor_frame)] ; [0 0 0 1]]);
    for radii = zone_radius_centers
        for alp = zone_angle_center_lines
            [centr_x , centr_y] = pol2cart(alp, radii );
            trasform_cell{end+1} = compute_contact_transform([centr_x; centr_y], silicon_sphere_radius, z_coord_sphere_frame_wrt_calib_sensor_frame);
        end
    end
    end
"""
from __future__ import annotations

from typing import Sequence

import numpy as np


def compute_contact_transform(
    centroid: Sequence[float],
    silicon_sphere_radius: float,
    z_coord_sphere_frame_wrt_calib_sensor_frame: float,
) -> np.ndarray:
    """Compute cont_T_sc: the pose of the calib-sensor frame w.r.t. the contact frame.

    Parameters
    ----------
    centroid: (2,) — [x, y] centroid on the tactile map, in meters.
    silicon_sphere_radius: R in the paper, meters.
    z_coord_sphere_frame_wrt_calib_sensor_frame: offset along z of the
        undeformed-sphere-center frame w.r.t. the calibration sensor
        frame, in meters (this is `finger_info.z_coord_sphere_frame_wrt_calib_sensor_frame`).

    Returns
    -------
    np.ndarray, shape (4, 4) homogeneous transform: cont_T_sc.
    """
    cx, cy = float(centroid[0]), float(centroid[1])
    r = float(silicon_sphere_radius)

    z_sq = r**2 - cx**2 - cy**2
    if z_sq < 0:
        raise ValueError(
            f"centroid ({cx}, {cy}) lies outside the sphere of radius {r}: "
            f"R^2 - x^2 - y^2 = {z_sq} < 0"
        )
    sf_p_cont = np.array([cx, cy, np.sqrt(z_sq)])

    n_hat = sf_p_cont / r

    sc_x_cont = np.array([1.0, 0.0, 0.0]) - n_hat[0] * n_hat
    sc_x_cont = sc_x_cont / np.linalg.norm(sc_x_cont)

    sc_y_cont = np.array([0.0, 1.0, 0.0]) - n_hat[1] * n_hat
    sc_y_cont = sc_y_cont / np.linalg.norm(sc_y_cont)

    sc_r_cont = np.column_stack([sc_x_cont, sc_y_cont, n_hat])  # 3x3

    sc_t_sf = np.eye(4)
    sc_t_sf[:3, 3] = [0.0, 0.0, z_coord_sphere_frame_wrt_calib_sensor_frame]

    sc_p_cont_tilde = sc_t_sf @ np.append(sf_p_cont, 1.0)  # (4,)

    sc_t_cont = np.eye(4)
    sc_t_cont[:3, :3] = sc_r_cont
    sc_t_cont[:3, 3] = sc_p_cont_tilde[:3]

    cont_t_sc = np.linalg.inv(sc_t_cont)
    return cont_t_sc


def compute_zone_central_transforms(
    zone_radius_centers: Sequence[float],
    silicon_sphere_radius: float,
    z_coord_sphere_frame_wrt_calib_sensor_frame: float,
    zone_angle_center_lines: Sequence[float],
) -> list[np.ndarray]:
    """Compute the nominal cont_T_sc for the central zone and every
    (radius, angle) zone center, in the same order the MATLAB code
    fills `trasform_cell` (central zone first, then radius-major /
    angle-minor loop order).

    Returns
    -------
    list of (4,4) np.ndarray, length = 1 + len(zone_radius_centers) * len(zone_angle_center_lines)
    """
    transforms: list[np.ndarray] = []

    central = np.eye(4)
    central[:3, 3] = [0.0, 0.0, -(silicon_sphere_radius + z_coord_sphere_frame_wrt_calib_sensor_frame)]
    transforms.append(central)

    for radii in zone_radius_centers:
        for alp in zone_angle_center_lines:
            centr_x = radii * np.cos(alp)
            centr_y = radii * np.sin(alp)
            transforms.append(
                compute_contact_transform(
                    [centr_x, centr_y],
                    silicon_sphere_radius,
                    z_coord_sphere_frame_wrt_calib_sensor_frame,
                )
            )

    return transforms

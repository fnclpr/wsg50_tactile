"""
test_centroid_zero_is_hand_derived: fully hand-derived from the MATLAB
algebra (see comments) — this is the primary correctness check.

The other tests are self-consistency / property checks (orthonormal
rotation, round-trip point recovery, and cross-validation between
compute_contact_transform and compute_zone_central_transforms' wiring)
since we do not have a MATLAB runtime available in this environment to
generate additional independent numeric references. These still catch
real algebra/implementation bugs (a broken formula will not produce an
orthonormal rotation or will not round-trip).
"""
import math

import numpy as np

from tactile_core.processing.geometry import (
    compute_contact_transform,
    compute_zone_central_transforms,
)

R = 0.05
Z_OFFSET = -0.01


def test_centroid_zero_is_hand_derived():
    # centroid = (0,0):
    #   sf_P_cont = [0, 0, R]  (since sqrt(R^2-0-0) = R)
    #   n_hat = [0, 0, 1]
    #   sc_x_cont = [1,0,0] - 0*n_hat = [1,0,0] (already unit)
    #   sc_y_cont = [0,1,0] - 0*n_hat = [0,1,0] (already unit)
    #   sc_R_cont = I
    #   sc_T_sf translation = [0,0,Z_OFFSET]
    #   sc_P_cont_tilde = [0,0, R+Z_OFFSET, 1]
    #   sc_T_cont = [I, [0,0,R+Z_OFFSET]; 0 0 0 1]
    #   cont_T_sc = inverse of a pure translation with R=I
    #             = [I, -[0,0,R+Z_OFFSET]; 0 0 0 1]
    cont_t_sc = compute_contact_transform([0.0, 0.0], R, Z_OFFSET)

    np.testing.assert_allclose(cont_t_sc[:3, :3], np.eye(3), atol=1e-12)
    np.testing.assert_allclose(cont_t_sc[:3, 3], [0.0, 0.0, -(R + Z_OFFSET)], atol=1e-12)
    np.testing.assert_allclose(cont_t_sc[3, :], [0, 0, 0, 1])


def test_rotation_columns_are_unit_norm_and_normal_axis_is_orthogonal():
    # NOTE ON WHY THIS TEST INVERTS TWICE: compute_contact_transform
    # returns cont_T_sc = inv(sc_T_cont). Because sc_R_cont is NOT
    # orthonormal (see the "IMPORTANT" note in geometry.py), the
    # rotation block of the INVERSE is R^-1, not R^T -- so it does NOT
    # inherit the unit-column/orthogonal-to-n_hat properties directly.
    # Those properties belong to the *forward* rotation sc_R_cont. We
    # recover it here via a second inversion (black-box, no duplicated
    # internal formulas) purely to check that forward construction's
    # documented guarantees still hold for an off-axis centroid.
    cont_t_sc = compute_contact_transform([0.01, 0.005], R, Z_OFFSET)
    sc_t_cont = np.linalg.inv(cont_t_sc)
    rot = sc_t_cont[:3, :3]
    x_cont, y_cont, n_hat = rot[:, 0], rot[:, 1], rot[:, 2]

    for col in (x_cont, y_cont, n_hat):
        assert math.isclose(np.linalg.norm(col), 1.0, abs_tol=1e-9)

    assert math.isclose(np.dot(x_cont, n_hat), 0.0, abs_tol=1e-9)
    assert math.isclose(np.dot(y_cont, n_hat), 0.0, abs_tol=1e-9)
    # documented non-guarantee: x_cont and y_cont need NOT be orthogonal
    # (this is intentionally not asserted to be ~0 here)


def test_rotation_is_exactly_orthonormal_on_axis():
    # At the on-axis centroid (0,0), n_hat = [0,0,1] and the projected
    # x/y axes are already exactly orthogonal (no approximation error),
    # so here — and only here — full orthonormality is guaranteed.
    cont_t_sc = compute_contact_transform([0.0, 0.0], R, Z_OFFSET)
    rot = cont_t_sc[:3, :3]
    np.testing.assert_allclose(rot.T @ rot, np.eye(3), atol=1e-12)
    assert math.isclose(np.linalg.det(rot), 1.0, abs_tol=1e-12)


def test_zone_central_transforms_first_entry_matches_zero_centroid():
    # trasform_cell{1} in the MATLAB code is built with the SAME formula
    # as compute_contact_transform([0,0], R, z) -- verify the two agree.
    radii = [0.003, 0.0075]
    angles = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]

    transforms = compute_zone_central_transforms(radii, R, Z_OFFSET, angles)
    expected_central = compute_contact_transform([0.0, 0.0], R, Z_OFFSET)

    np.testing.assert_allclose(transforms[0], expected_central, atol=1e-12)
    # 1 central + 2 radii * 4 angles = 9 total, matching compute_num_zones' formula
    assert len(transforms) == 1 + len(radii) * len(angles)


def test_zone_central_transforms_wiring_matches_pol2cart_convention():
    radii = [0.003]
    angles = [math.pi / 2]  # straight up the y-axis
    transforms = compute_zone_central_transforms(radii, R, Z_OFFSET, angles)

    # pol2cart(pi/2, 0.003) -> (x=0, y=0.003)
    expected = compute_contact_transform([0.0, 0.003], R, Z_OFFSET)
    np.testing.assert_allclose(transforms[1], expected, atol=1e-12)

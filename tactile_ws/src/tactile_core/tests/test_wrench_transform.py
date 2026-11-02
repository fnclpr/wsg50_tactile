"""
All reference values here are hand-derived from the MATLAB formula:

    t_wrench(1:3) = R * s_wrench(1:3)
    t_wrench(4:6) = R * s_wrench(4:6) + cross(p, t_wrench(1:3))
"""
import numpy as np

from tactile_core.processing.wrench_transform import transform_wrench


def test_identity_transform_leaves_wrench_unchanged():
    t = np.eye(4)
    wrench = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    result = transform_wrench(t, wrench)
    np.testing.assert_allclose(result, wrench)


def test_pure_translation_adds_moment_from_force():
    # R = I, p = [0,0,1]
    t = np.eye(4)
    t[:3, 3] = [0.0, 0.0, 1.0]
    wrench = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    # f_t = [1,0,0]
    # tau_t = [0,0,0] + cross([0,0,1],[1,0,0]) = [0,1,0]
    result = transform_wrench(t, wrench)
    np.testing.assert_allclose(result, [1.0, 0.0, 0.0, 0.0, 1.0, 0.0], atol=1e-12)


def test_pure_rotation_90deg_about_z():
    # R = Rz(90deg) = [[0,-1,0],[1,0,0],[0,0,1]], p = 0
    t = np.eye(4)
    t[:3, :3] = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    wrench = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    # f_t = R @ [1,0,0] = [0,1,0]
    # tau_t = R @ [0,0,1] + cross(0, f_t) = [0,0,1]
    result = transform_wrench(t, wrench)
    np.testing.assert_allclose(result, [0.0, 1.0, 0.0, 0.0, 0.0, 1.0], atol=1e-12)

"""
Reference values hand-derived from:
    compute_max_ft.m:  maxFt = mu*abs(fn)
    compute_max_taun.m: maxM = alpha*(abs(fn)^(gamma+1))
    compute_wrench_plot_point.m (see module docstring in
        tactile_core/processing/limit_surface.py for the full formula)
"""
import math

import numpy as np

from tactile_core.processing.limit_surface import (
    compute_max_ft,
    compute_max_taun,
    compute_wrench_plot_point,
)


def test_compute_max_ft():
    assert compute_max_ft(fn=-8.0, mu=0.5) == 4.0
    assert compute_max_ft(fn=3.0, mu=1.0) == 3.0


def test_compute_max_taun():
    # alpha * |fn|^(gamma+1) = 2 * 8^1.5 = 2 * 22.627417... = 45.254834...
    result = compute_max_taun(fn=-8.0, alpha=2.0, gamma=0.5)
    expected = 2.0 * (8.0 ** 1.5)
    assert math.isclose(result, expected, rel_tol=1e-12)
    assert math.isclose(result, 45.254833995939045, rel_tol=1e-9)


def test_compute_wrench_plot_point_identity_transform():
    # transform = identity -> transform_wrench leaves wrench unchanged,
    # and transform[2,2] (== R[2,2]) = 1
    transform = np.eye(4)
    fz_nominal = 10.0
    mu, alpha, gamma = 0.5, 2.0, 0.5

    # contact_fn_nominal = 1 * 10 = 10
    # max_ft_nominal   = 0.5 * 10 = 5
    # max_taun_nominal = 2 * 10^1.5 = 2*31.6227766... = 63.2455532...
    # Chosen wrench components so the normalized result is clean:
    wrench = np.array([2.5, 1.25, 10.0, 0.0, 0.0, 6.324555320336759])

    result = compute_wrench_plot_point(wrench, fz_nominal, transform, mu, alpha, gamma)

    np.testing.assert_allclose(result, [0.5, 0.25, 0.1], atol=1e-9)

import numpy as np
import pytest

from tactile_calibration.pca_compression import fit_pca


def _data(n=500, seed=0):
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(n, 3))
    mixing = rng.normal(size=(3, 25))
    return latent @ mixing + 0.01 * rng.normal(size=(n, 25)) + 0.5


def test_matches_legacy_formula():
    x = _data()
    m = fit_pca(x, 15)
    per_sample = np.stack([m.u_reduce.T @ (xi - m.mean) for xi in x])
    np.testing.assert_allclose(m.transform(x), per_sample, atol=1e-12)


def test_orthonormal_columns():
    m = fit_pca(_data(), 15)
    np.testing.assert_allclose(m.u_reduce.T @ m.u_reduce, np.eye(15), atol=1e-10)


def test_full_rank_reconstruction_exact():
    x = _data()
    m = fit_pca(x, 25)
    np.testing.assert_allclose(m.inverse_transform(m.transform(x)), x, atol=1e-9)


def test_low_rank_captures_variance():
    m = fit_pca(_data(), 3)
    assert m.explained_variance_ratio.sum() > 0.99


def test_broken_cells_are_ignored():
    x = _data()
    x_corrupt = x.copy()
    x_corrupt[:, 4] = 99.0
    m = fit_pca(x_corrupt, 10, broken_cells=(4, 6))
    assert np.all(m.u_reduce[[4, 6], :] == 0.0)
    assert np.all(m.mean[[4, 6]] == 0.0)
    y1 = m.transform(x)
    x2 = x.copy()
    x2[:, 4] = -50.0
    np.testing.assert_allclose(m.transform(x2), y1, atol=1e-12)


def test_deterministic():
    x = _data()
    a, b = fit_pca(x, 15), fit_pca(x, 15)
    np.testing.assert_array_equal(a.u_reduce, b.u_reduce)


def test_invalid_inputs():
    x = _data()
    with pytest.raises(ValueError):
        fit_pca(x, 0)
    with pytest.raises(ValueError):
        fit_pca(x, 26)
    with pytest.raises(ValueError):
        fit_pca(x, 5, broken_cells=(25,))
    bad = x.copy()
    bad[0, 0] = np.nan
    with pytest.raises(ValueError):
        fit_pca(bad, 5)
    with pytest.raises(ValueError):
        fit_pca(x, 15).transform(np.zeros(24))

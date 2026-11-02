import numpy as np
import pytest

from tactile_calibration.io_formats import export_model, load_model
from tactile_calibration.training import TrainConfig, split_indices, train_model

from .conftest_data import synthetic

FAST = dict(hidden_layers=(24, 24), max_epochs=250, max_fail=60, batch_size=128,
            learning_rate=3e-3, seed=3)


def test_trains_and_generalizes():
    v, y = synthetic()
    m = train_model(v, y, TrainConfig(n_components=10, **FAST))
    r2 = np.array(m.metrics["test"]["r2"])
    assert np.isnan(r2[4])                      # constant column -> NaN, not a crash
    assert np.nanmin(np.delete(r2, 4)) > 0.9
    assert np.all(np.isfinite(m.predict(v)))
    assert m.metadata["split_sizes"]["train"] + m.metadata["split_sizes"]["validation"] \
        + m.metadata["split_sizes"]["test"] == m.metadata["n_real_samples"] + m.metadata["n_zero_samples_added"]


def test_deterministic_given_seed():
    v, y = synthetic(n=400)
    cfg = TrainConfig(n_components=8, hidden_layers=(10,), max_epochs=30, seed=5)
    a, b = train_model(v, y, cfg), train_model(v, y, cfg)
    for wa, wb in zip(a.weights, b.weights):
        np.testing.assert_array_equal(wa, wb)


def test_no_pca_with_broken_cells(tmp_path):
    v, y = synthetic(n=600)
    cfg = TrainConfig(n_components=0, hidden_layers=(12,), max_epochs=40, seed=1)
    m = train_model(v, y, cfg, broken_cells=(4, 9))
    assert np.all(m.weights[0][:, [4, 9]] == 0.0)
    assert m.input_min[4] == -1 and m.input_max[9] == 1
    v2 = v[:50].copy()
    v2[:, 4] = 123.0
    np.testing.assert_allclose(m.predict(v2), m.predict(v[:50]), atol=1e-12)
    # exported file still takes 25 inputs and matches
    p = export_model(m, tmp_path, "net_file")["net_file"]
    np.testing.assert_allclose(load_model(p).predict(v[:50]), m.predict(v[:50]), rtol=1e-7, atol=1e-7)


def test_pca_with_broken_cells_ignores_them():
    v, y = synthetic(n=600)
    m = train_model(v, y, TrainConfig(n_components=8, hidden_layers=(10,), max_epochs=30), broken_cells=(2,))
    v2 = v[:20].copy()
    v2[:, 2] = -77.0
    np.testing.assert_allclose(m.predict(v2), m.predict(v[:20]), atol=1e-12)


def test_callback_can_cancel():
    v, y = synthetic(n=300)
    calls = []

    def cb(epoch, tr, va, best):
        calls.append(epoch)
        return epoch >= 3

    m = train_model(v, y, TrainConfig(n_components=5, hidden_layers=(6,), max_epochs=100), callback=cb)
    assert calls == [1, 2, 3]
    assert m.metadata["stop_reason"] == "cancelled"


def test_early_stopping_max_fail():
    v, y = synthetic(n=300)
    m = train_model(v, y, TrainConfig(n_components=5, hidden_layers=(6,), max_epochs=2000,
                                      max_fail=3, learning_rate=0.5))
    assert m.metadata["epochs_run"] < 2000


def test_split_indices_partition():
    tr, va, te = split_indices(100, (0.5, 0.4, 0.1), seed=0)
    assert len(tr) == 50 and len(va) == 40 and len(te) == 10
    assert sorted(np.concatenate([tr, va, te]).tolist()) == list(range(100))


def test_config_validation():
    for bad in (dict(split=(0.5, 0.4, 0.2)), dict(split=(1.0, 0.0, 0.0)), dict(n_components=-1),
                dict(zero_fraction=1.0), dict(hidden_layers=(0,)), dict(learning_rate=0)):
        with pytest.raises(ValueError):
            TrainConfig(**bad).validate()


def test_bad_data_rejected():
    v, y = synthetic(n=100)
    with pytest.raises(ValueError):
        train_model(v[:, :24], y)
    with pytest.raises(ValueError):
        train_model(v, y[:, :5])
    bad = v.copy()
    bad[0, 0] = np.nan
    with pytest.raises(ValueError):
        train_model(bad, y)
    with pytest.raises(ValueError):
        train_model(v, y, broken_cells=(25,))
    with pytest.raises(ValueError):
        train_model(v[:10], y[:10])

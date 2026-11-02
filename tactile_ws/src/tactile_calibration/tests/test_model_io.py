import numpy as np
import pytest
import yaml

from tactile_calibration.io_formats import (NET_FILE_NAME, export_model,
                                            load_model, parse_formats,
                                            read_net_file, write_net_file)
from tactile_calibration.model import TrainedModel
from tactile_calibration.pca_compression import fit_pca


def _model(with_pca=True, seed=1, hidden=(7, 5), n_out=6):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(200, 25))
    pca = fit_pca(v, 6, broken_cells=(3,)) if with_pca else None
    n_in = 6 if with_pca else 25
    sizes = [n_in, *hidden, n_out]
    W = [rng.normal(size=(sizes[i + 1], sizes[i])) for i in range(len(sizes) - 1)]
    b = [rng.normal(size=sizes[i + 1]) for i in range(len(sizes) - 1)]
    acts = ["tanh"] * (len(W) - 1) + ["linear"]
    return TrainedModel(
        n_input=25, pca=pca,
        input_min=-rng.uniform(1, 2, n_in), input_max=rng.uniform(1, 2, n_in),
        weights=W, biases=b, activations=acts,
        target_min=-rng.uniform(1, 3, n_out), target_max=rng.uniform(1, 3, n_out),
        broken_cells=(3,) if with_pca else (),
        metrics={"x": 1.0}, metadata={"note": "t"}), v


def test_tansig_equals_tanh():
    x = np.linspace(-5, 5, 101)
    np.testing.assert_allclose(2.0 / (1.0 + np.exp(-2.0 * x)) - 1.0, np.tanh(x), atol=1e-14)


@pytest.mark.parametrize("with_pca", [True, False])
def test_net_file_layout_matches_legacy(tmp_path, with_pca):
    m, _ = _model(with_pca)
    p = write_net_file(m, tmp_path / NET_FILE_NAME)
    lines = p.read_text().splitlines()
    vals = [float(s) for s in lines]
    assert all(len(s.split("E")) == 2 for s in lines)  # %.10E, one number per line
    n_in = 6 if with_pca else 25
    expected = 0
    if with_pca:
        expected += 3 + 25 + 25 * 6
    expected += 2 + 2 * n_in
    sizes = [n_in, 7, 5, 6]
    for i in range(3):
        expected += 4 + sizes[i + 1] * sizes[i] + sizes[i + 1]
    expected += 2 + 2 * 6 + 1
    assert len(vals) == expected
    assert vals[0] == (1.0 if with_pca else 2.0)
    assert vals[-1] == 0.0
    if with_pca:
        assert vals[1:3] == [25.0, 6.0]
        # Ureduce stored row-major: first row of U right after the mean
        np.testing.assert_allclose(vals[3 + 25:3 + 25 + 6], m.pca.u_reduce[0], rtol=1e-9, atol=1e-12)


@pytest.mark.parametrize("with_pca", [True, False])
def test_net_file_roundtrip_predictions(tmp_path, with_pca):
    m, v = _model(with_pca)
    p = write_net_file(m, tmp_path / NET_FILE_NAME)
    m2 = read_net_file(p)
    np.testing.assert_allclose(m2.predict(v), m.predict(v), rtol=1e-8, atol=1e-8)


def test_npz_and_yaml_roundtrip_exact(tmp_path):
    m, v = _model(True)
    out = export_model(m, tmp_path, "all")
    assert set(out) == {"net_file", "npz", "yaml"}
    for path in (out["npz"], out["yaml"]):
        m2 = load_model(path)
        np.testing.assert_array_equal(m2.predict(v), m.predict(v))
        assert m2.broken_cells == (3,)
        assert m2.metrics == {"x": 1.0}
    assert load_model(tmp_path).n_input == 25  # directory -> npz
    assert (tmp_path / "training_report.yaml").exists()


def test_npz_checksum_detects_tampering(tmp_path):
    m, _ = _model(True)
    out = export_model(m, tmp_path, "npz")
    with open(out["npz"], "ab") as f:
        f.write(b"x")
    with pytest.raises(ValueError):
        load_model(out["npz"])


def test_unsupported_version_rejected(tmp_path):
    m, _ = _model(True)
    out = export_model(m, tmp_path, "yaml")
    doc = yaml.safe_load(open(out["yaml"]))
    doc["format_version"] = 99
    yaml.safe_dump(doc, open(out["yaml"], "w"))
    with pytest.raises(ValueError):
        load_model(out["yaml"])


def test_truncated_or_garbage_net_file_rejected(tmp_path):
    m, _ = _model(False)
    p = write_net_file(m, tmp_path / "n.txt")
    lines = p.read_text().splitlines()
    (tmp_path / "t.txt").write_text("\n".join(lines[:-5]) + "\n")
    with pytest.raises(ValueError):
        read_net_file(tmp_path / "t.txt")
    (tmp_path / "g.txt").write_text("7.0\n")
    with pytest.raises(ValueError):
        read_net_file(tmp_path / "g.txt")


def test_parse_formats():
    assert parse_formats("all") == ("net_file", "npz", "yaml")
    assert parse_formats("npz, net_file,npz") == ("npz", "net_file")
    with pytest.raises(ValueError):
        parse_formats("csv")


def test_invalid_model_shapes_rejected():
    m, _ = _model(True)
    with pytest.raises(ValueError):
        TrainedModel(n_input=25, pca=m.pca, input_min=m.input_min[:-1], input_max=m.input_max[:-1],
                     weights=m.weights, biases=m.biases, activations=m.activations,
                     target_min=m.target_min, target_max=m.target_max)
    with pytest.raises(ValueError):
        m.predict(np.zeros(24))

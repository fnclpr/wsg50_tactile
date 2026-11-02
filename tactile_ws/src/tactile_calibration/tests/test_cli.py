import numpy as np

from tactile_calibration.cli import main
from tactile_calibration.io_formats import load_model

from .conftest_data import synthetic


def test_cli_train_convert_predict(tmp_path, capsys):
    v, y = synthetic(n=500)
    data = tmp_path / "d.npz"
    np.savez(data, voltages=v, wrench=y, broken_cells=np.array([5]))
    out = tmp_path / "out"
    rc = main(["train", "--data", str(data), "--out-dir", str(out), "--formats", "all",
               "--pca", "6", "--hidden", "8x2", "--epochs", "20", "--quiet"])
    assert rc == 0
    assert (out / "NET_FILE.txt").exists() and (out / "model.npz").exists() and (out / "model.yaml").exists()
    m = load_model(out / "NET_FILE.txt")
    assert [w.shape[0] for w in m.weights] == [8, 8, 6]

    out2 = tmp_path / "conv"
    assert main(["convert", "--model", str(out / "NET_FILE.txt"), "--out-dir", str(out2),
                 "--formats", "npz"]) == 0
    assert (out2 / "model.npz").exists()

    np.savetxt(tmp_path / "in.csv", v[:3], delimiter=",")
    capsys.readouterr()
    assert main(["predict", "--model", str(out / "model.npz"), "--inputs", str(tmp_path / "in.csv")]) == 0
    got = np.loadtxt(capsys.readouterr().out.splitlines(), delimiter=",")
    np.testing.assert_allclose(got, load_model(out / "model.npz").predict(v[:3]), rtol=1e-8, atol=1e-8)


def test_cli_errors_return_nonzero(tmp_path, capsys):
    assert main(["train", "--data", str(tmp_path / "missing.npz"), "--out-dir", str(tmp_path),
                 "--formats", "csv"]) == 1
    v, y = synthetic(n=100)
    np.savez(tmp_path / "d.npz", voltages=v, wrench=y)
    assert main(["train", "--data", str(tmp_path / "d.npz"), "--out-dir", str(tmp_path),
                 "--broken-cells", "26", "--epochs", "2"]) == 1
    assert "ERROR" in capsys.readouterr().err

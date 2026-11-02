"""Command line: train / convert / predict.

    ros2 run tactile_calibration tactile_train train --data calibration/session --out-dir calibration/F401
    python3 -m tactile_calibration.cli convert --model calibration/F401/NET_FILE.txt --out-dir out --formats npz,yaml
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

import numpy as np

from .data import load_arrays
from .io_formats import export_model, load_model, parse_formats
from .training import TrainConfig, train_model


def _hidden(s: str) -> tuple:
    s = s.strip().lower()
    if "x" in s:
        n, k = s.split("x")
        return (int(n),) * int(k)
    return tuple(int(p) for p in s.split(",") if p)


def _floats(s: str) -> tuple:
    return tuple(float(p) for p in s.split(","))


def _ints(s: str) -> tuple:
    return tuple(int(p) for p in s.split(",") if p)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tactile_train", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train", help="train a calibration model and export it")
    t.add_argument("--data", required=True, help="ProjectData base path (.h5/.yaml) or .npz")
    t.add_argument("--out-dir", required=True)
    t.add_argument("--formats", default="net_file", help="net_file,npz,yaml or all (default net_file)")
    t.add_argument("--pca", type=int, default=15, help="PCA components, 0 = no PCA (default 15)")
    t.add_argument("--hidden", type=_hidden, default=(90,) * 6, help="'90x6' or '50,25,10'")
    t.add_argument("--split", type=_floats, default=(0.5, 0.4, 0.1), help="train,val,test fractions")
    t.add_argument("--zero-fraction", type=float, default=0.006)
    t.add_argument("--epochs", type=int, default=1000)
    t.add_argument("--max-fail", type=int, default=150)
    t.add_argument("--batch-size", type=int, default=256)
    t.add_argument("--lr", type=float, default=1e-3)
    t.add_argument("--l2", type=float, default=0.0)
    t.add_argument("--seed", type=int, default=0)
    t.add_argument("--decimation-radius", type=float, default=0.0,
                   help="bubble decimation radius (ProjectData only; 0 = off)")
    t.add_argument("--broken-cells", type=_ints, default=None,
                   help="1-based taxel numbers to ignore, e.g. 5,7 (overrides the data file)")
    t.add_argument("--quiet", action="store_true")

    c = sub.add_parser("convert", help="convert a saved model to other formats")
    c.add_argument("--model", required=True)
    c.add_argument("--out-dir", required=True)
    c.add_argument("--formats", required=True)

    r = sub.add_parser("predict", help="run a saved model on a CSV of 25-voltage rows")
    r.add_argument("--model", required=True)
    r.add_argument("--inputs", required=True, help="CSV, one 25-value row per sample")
    r.add_argument("--output", default=None, help="CSV output (default: stdout)")
    return p


def _cmd_train(a) -> int:
    parse_formats(a.formats)  # fail early on a typo
    v, y, broken, info = load_arrays(a.data, a.decimation_radius,
                                     None if a.broken_cells is None else a.broken_cells)
    cfg = TrainConfig(n_components=a.pca, hidden_layers=a.hidden, split=a.split,
                      zero_fraction=a.zero_fraction, max_epochs=a.epochs,
                      max_fail=a.max_fail, batch_size=a.batch_size,
                      learning_rate=a.lr, l2=a.l2, seed=a.seed)

    def progress(epoch, tr, va, best):
        if not a.quiet and (epoch == 1 or epoch % 10 == 0):
            print(f"epoch {epoch:5d}  train_mse={tr:.5f}  val_mse={va:.5f}  best={best:.5f}",
                  file=sys.stderr)
        return False

    print(f"samples={v.shape[0]} broken_cells(1-based)={info['broken_cells_1based']}", file=sys.stderr)
    model = train_model(v, y, cfg, broken, progress)
    model.metadata["data"] = info
    written = export_model(model, a.out_dir, a.formats)
    for k, p in written.items():
        print(f"{k}: {p}")
    for split in ("train", "validation", "test"):
        m = model.metrics.get(split)
        if m:
            print(f"[{split}] n={m['n_samples']} RMSE=" + " ".join(f"{v_:.4g}" for v_ in m["rmse"]))
    print(f"stop_reason={model.metadata['stop_reason']} epochs={model.metadata['epochs_run']}")
    return 0


def _cmd_convert(a) -> int:
    model = load_model(a.model)
    for k, p in export_model(model, a.out_dir, a.formats).items():
        print(f"{k}: {p}")
    return 0


def _cmd_predict(a) -> int:
    model = load_model(a.model)
    x = np.atleast_2d(np.loadtxt(a.inputs, delimiter=","))
    out = model.predict(x)
    if a.output:
        np.savetxt(a.output, out, delimiter=",", fmt="%.10e")
    else:
        np.savetxt(sys.stdout, out, delimiter=",", fmt="%.10e")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    a = _build_parser().parse_args(argv)
    try:
        return {"train": _cmd_train, "convert": _cmd_convert, "predict": _cmd_predict}[a.cmd](a)
    except (ValueError, OSError, ImportError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

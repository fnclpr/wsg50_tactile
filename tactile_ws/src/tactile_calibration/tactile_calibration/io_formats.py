"""Model persistence: legacy NET_FILE.txt (default), NPZ(+metadata.yaml), YAML.

NET_FILE.txt layout (from gen_net_files.m, read by ANN_File_Reader.cpp).
One number per line, format %.10E:

    [1  n_in  r   mean[n_in]  Ureduce[n_in x r, row-major]]      optional PCA
     2  n     min[n]  max[n]                                     input MapMinMax
    (4  n_in  n_out  act  W[n_out x n_in, row-major]  b[n_out])* fully connected
                                                                 act: 1=tansig 2=purelin
     3  n     min[n]  max[n]                                     reverse MapMinMax
     0                                                           terminator
"""
from __future__ import annotations

import datetime
import hashlib
from pathlib import Path
from typing import Iterable, Union

import numpy as np
import yaml

from .model import TrainedModel
from .pca_compression import PcaModel

FORMAT_VERSION = 1
PCA_CODE, MINMAX_CODE, MINMAX_REV_CODE, FC_CODE, END_CODE = 1, 2, 3, 4, 0
ACT_TO_CODE = {"tanh": 1, "linear": 2}
CODE_TO_ACT = {v: k for k, v in ACT_TO_CODE.items()}
ALL_FORMATS = ("net_file", "npz", "yaml")
NET_FILE_NAME = "NET_FILE.txt"


# ---------------------------------------------------------------- NET_FILE
def write_net_file(model: TrainedModel, path: Union[str, Path]) -> Path:
    path = Path(path)
    t: list = []

    def put(a) -> None:
        t.extend(float(v) for v in np.asarray(a, dtype=np.float64).ravel(order="C"))

    if model.pca is not None:
        put([PCA_CODE, model.n_input, model.pca.n_components])
        put(model.pca.mean)
        put(model.pca.u_reduce)  # (n_in x r) row-major == MATLAB's fprintf(Ureduce')
    put([MINMAX_CODE, model.input_min.size])
    put(model.input_min)
    put(model.input_max)
    for w, b, a in zip(model.weights, model.biases, model.activations):
        put([FC_CODE, w.shape[1], w.shape[0], ACT_TO_CODE[a]])
        put(w)  # (n_out x n_in) row-major == fprintf(W')
        put(b)
    put([MINMAX_REV_CODE, model.target_min.size])
    put(model.target_min)
    put(model.target_max)
    put([END_CODE])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{v:.10E}\n" for v in t))
    return path


def read_net_file(path: Union[str, Path]) -> TrainedModel:
    """Parse a NET_FILE.txt the way ANN_File_Reader.cpp does, restricted to
    the layer order this package produces. broken_cells/metrics are not stored
    in the file and come back empty."""
    vals = np.array(Path(path).read_text().split(), dtype=np.float64)
    pos = 0

    def take(n: int) -> np.ndarray:
        nonlocal pos
        if pos + n > vals.size:
            raise ValueError("NET_FILE truncated")
        out = vals[pos:pos + n]
        pos += n
        return out

    def take_int() -> int:
        return int(take(1)[0])

    pca = None
    n_input = None
    code = take_int()
    if code == PCA_CODE:
        n_in, r = take_int(), take_int()
        mean = take(n_in)
        u = take(n_in * r).reshape(n_in, r)
        pca = PcaModel(mean=mean, u_reduce=u,
                       explained_variance_ratio=np.full(r, np.nan), broken_cells=())
        n_input = n_in
        code = take_int()
    if code != MINMAX_CODE:
        raise ValueError(f"expected input MapMinMax (2), got layer code {code}")
    n = take_int()
    in_min, in_max = take(n), take(n)
    if n_input is None:
        n_input = n

    weights, biases, acts = [], [], []
    code = take_int()
    while code == FC_CODE:
        n_in, n_out, act = take_int(), take_int(), take_int()
        if act not in CODE_TO_ACT:
            raise ValueError(f"unknown activation code {act}")
        weights.append(take(n_out * n_in).reshape(n_out, n_in))
        biases.append(take(n_out))
        acts.append(CODE_TO_ACT[act])
        code = take_int()
    if code != MINMAX_REV_CODE:
        raise ValueError(f"expected reverse MapMinMax (3), got layer code {code}")
    n = take_int()
    t_min, t_max = take(n), take(n)
    if take_int() != END_CODE:
        raise ValueError("missing terminator (0)")
    if pos != vals.size:
        raise ValueError("trailing data after terminator")
    return TrainedModel(n_input=n_input, pca=pca, input_min=in_min, input_max=in_max,
                        weights=weights, biases=biases, activations=acts,
                        target_min=t_min, target_max=t_max)


# ------------------------------------------------------------------ helpers
def _builtin(o):
    if isinstance(o, dict):
        return {str(k): _builtin(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_builtin(v) for v in o]
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.generic):
        return o.item()
    return o


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _structure(model: TrainedModel) -> dict:
    return {
        "format_version": FORMAT_VERSION,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "n_input": model.n_input,
        "n_output": model.n_output,
        "pca_components": model.pca.n_components if model.pca is not None else 0,
        "layer_sizes": [int(w.shape[0]) for w in model.weights],
        "activations": list(model.activations),
        "broken_cells_0based": list(model.broken_cells),
        "metrics": _builtin(model.metrics),
        "metadata": _builtin(model.metadata),
    }


def _arrays(model: TrainedModel) -> dict:
    d = {"input_min": model.input_min, "input_max": model.input_max,
         "target_min": model.target_min, "target_max": model.target_max}
    if model.pca is not None:
        d["pca_mean"] = model.pca.mean
        d["pca_u_reduce"] = model.pca.u_reduce
        d["pca_explained_variance_ratio"] = model.pca.explained_variance_ratio
    for i, (w, b) in enumerate(zip(model.weights, model.biases)):
        d[f"W{i}"], d[f"b{i}"] = w, b
    return d


def _build(struct: dict, arr) -> TrainedModel:
    pca = None
    if struct["pca_components"] > 0:
        pca = PcaModel(mean=np.array(arr["pca_mean"], dtype=np.float64),
                       u_reduce=np.array(arr["pca_u_reduce"], dtype=np.float64),
                       explained_variance_ratio=np.array(arr["pca_explained_variance_ratio"], dtype=np.float64),
                       broken_cells=tuple(struct["broken_cells_0based"]))
    n_layers = len(struct["layer_sizes"])
    return TrainedModel(
        n_input=struct["n_input"], pca=pca,
        input_min=np.array(arr["input_min"], dtype=np.float64),
        input_max=np.array(arr["input_max"], dtype=np.float64),
        weights=[np.array(arr[f"W{i}"], dtype=np.float64) for i in range(n_layers)],
        biases=[np.array(arr[f"b{i}"], dtype=np.float64) for i in range(n_layers)],
        activations=list(struct["activations"]),
        target_min=np.array(arr["target_min"], dtype=np.float64),
        target_max=np.array(arr["target_max"], dtype=np.float64),
        broken_cells=tuple(struct["broken_cells_0based"]),
        metrics=struct.get("metrics", {}), metadata=struct.get("metadata", {}))


def _check_version(struct: dict) -> None:
    if struct.get("format_version") != FORMAT_VERSION:
        raise ValueError(f"unsupported format_version {struct.get('format_version')} "
                         f"(supported: {FORMAT_VERSION})")


# ---------------------------------------------------------------- NPZ / YAML
def write_npz(model: TrainedModel, out_dir: Union[str, Path]) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    npz = out_dir / "model.npz"
    np.savez(npz, **_arrays(model))
    struct = _structure(model)
    struct["npz_file"] = npz.name
    struct["npz_sha256"] = _sha256(npz)
    with open(out_dir / "metadata.yaml", "w") as f:
        yaml.safe_dump(struct, f, sort_keys=False)
    return npz


def read_npz(path: Union[str, Path]) -> TrainedModel:
    path = Path(path)
    if path.is_dir():
        path = path / "model.npz"
    meta = path.with_name("metadata.yaml")
    if not meta.exists():
        raise ValueError(f"metadata.yaml not found next to {path}")
    with open(meta) as f:
        struct = yaml.safe_load(f)
    _check_version(struct)
    if struct.get("npz_sha256") != _sha256(path):
        raise ValueError(f"{path.name} does not match the checksum in metadata.yaml")
    with np.load(path) as arr:
        return _build(struct, {k: arr[k] for k in arr.files})


def write_yaml(model: TrainedModel, out_dir: Union[str, Path]) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = _structure(model)
    doc["arrays"] = {k: np.asarray(v).tolist() for k, v in _arrays(model).items()}
    path = out_dir / "model.yaml"
    with open(path, "w") as f:
        yaml.safe_dump(doc, f, sort_keys=False)
    return path


def read_yaml(path: Union[str, Path]) -> TrainedModel:
    with open(path) as f:
        doc = yaml.safe_load(f)
    _check_version(doc)
    return _build(doc, doc["arrays"])


# ------------------------------------------------------------ public front end
def parse_formats(spec: Union[str, Iterable[str]]) -> tuple:
    items = spec.split(",") if isinstance(spec, str) else list(spec)
    items = [s.strip() for s in items if s.strip()]
    if items == ["all"]:
        return ALL_FORMATS
    bad = [s for s in items if s not in ALL_FORMATS]
    if bad or not items:
        raise ValueError(f"unknown format(s) {bad or items}; choose from {ALL_FORMATS} or 'all'")
    return tuple(dict.fromkeys(items))


def export_model(model: TrainedModel, out_dir: Union[str, Path],
                 formats: Union[str, Iterable[str]] = ("net_file",)) -> dict:
    """Write the model in the requested formats. Returns {format: path}."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for fmt in parse_formats(formats):
        if fmt == "net_file":
            written[fmt] = write_net_file(model, out_dir / NET_FILE_NAME)
        elif fmt == "npz":
            written[fmt] = write_npz(model, out_dir)
        else:
            written[fmt] = write_yaml(model, out_dir)
    if model.metrics or model.metadata:
        with open(out_dir / "training_report.yaml", "w") as f:
            yaml.safe_dump({"metrics": _builtin(model.metrics),
                            "metadata": _builtin(model.metadata)}, f, sort_keys=False)
    return written


def load_model(path: Union[str, Path]) -> TrainedModel:
    """Load by extension: .txt (NET_FILE), .npz or directory (NPZ), .yaml/.yml."""
    path = Path(path)
    if path.is_dir():
        return read_npz(path)
    ext = path.suffix.lower()
    if ext == ".txt":
        return read_net_file(path)
    if ext == ".npz":
        return read_npz(path)
    if ext in (".yaml", ".yml"):
        return read_yaml(path)
    raise ValueError(f"cannot infer model format from '{path}'")

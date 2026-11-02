# tactile_calibration (Steps 11-12)

ament_python package. Library + CLI; no ROS nodes yet.

| Module | Purpose |
|---|---|
| `pca_compression.py` | PCA, legacy formula `y = U^T (x - mean)`, broken-cell zero padding |
| `model.py` | `TrainedModel`: PCA -> MinMax -> tanh FC layers -> reverse MinMax; metrics |
| `training.py` | `TrainConfig`, `train_model()` (callback for GUI progress/cancel) |
| `io_formats.py` | `export_model()` / `load_model()`: `net_file` (default), `npz`, `yaml` |
| `data.py` | load a ProjectData session (needs `tactile_core`) or a plain `.npz` |
| `cli.py` | `tactile_train train / convert / predict` |

## Install
    cp -r tactile_calibration ~/tactile_ws/src/        # replaces the Step 11 version
    cd /workspace && colcon build --packages-select tactile_calibration --symlink-install
    source install/setup.bash
    python3 -m pytest src/tactile_calibration/tests -v     # expect 29 passed

## Train from the CLI
    ros2 run tactile_calibration tactile_train train \
        --data calibration/session --out-dir calibration/F401 \
        --formats net_file            # or: npz | yaml | net_file,npz | all
Useful options: `--pca 15` (0 = no PCA), `--hidden 90x6` or `50,25,10`, `--split 0.5,0.4,0.1`,
`--zero-fraction 0.006`, `--epochs`, `--max-fail 150`, `--broken-cells 5,7` (1-based),
`--decimation-radius R`, `--seed`.

`--data` is either a ProjectData base path (`calibration/session` -> `.h5` + `.yaml`) or an `.npz`
with `voltages (N,25)`, `wrench (N,6)` and optional `broken_cells` (1-BASED, as in ProjectData).

## From Python / a GUI
    from tactile_calibration import TrainConfig, train_model, export_model, load_arrays
    v, y, broken0, info = load_arrays("calibration/session")
    model = train_model(v, y, TrainConfig(n_components=15), broken0,
                        callback=lambda ep, tr, va, best: False)   # return True to cancel
    export_model(model, "calibration/F401", formats="net_file")    # or ("net_file","npz")
    model.predict(voltages_25)            # -> (6,) wrench

## Output files
- `NET_FILE.txt`: legacy format, read by `uclv_tactile_wrench` (`finger_calibration_file` parameter).
- `model.npz` + `metadata.yaml`: arrays + structure, metrics, config, SHA-256 of the npz (checked on load).
- `model.yaml`: the same, self-contained and human readable.
- `training_report.yaml`: metrics (RMSE, MAE, max error, R^2 per component, train/validation/test) and config.

## Things to know (ENGINEERING DECISIONS / limits)
- Optimizer is Adam with legacy-style early stopping (validation patience = `max_fail`, best weights
  restored). The legacy `trainscg` is not in scikit-learn, so results are not bit-identical to MATLAB.
- Defaults come from `the_train.m` (90x6 network, 50/40/10 split, 0.6 % zero samples). The PCA default of
  15 comes from `the_cross_train.m`/the project summary and is not yet checked against the paper.
- PCA and the MinMax scalers are fitted on the whole set before the split (as MATLAB's `train()` does).
- Decimation, if enabled, is the paper's unnormalized bubble algorithm (the legacy `sun_train_decim` is missing).
- `NET_FILE.txt` does not store broken cells or metrics. Use npz/yaml if you need them back.
- A constant feature/target column gets range (c-1, c+1) instead of dividing by zero.
- No acceptance thresholds are hard-coded: PASS/FAIL criteria must come from the paper or from you.

## Optional: cross-check against the real C++ reader
`tools/check_net_file.cpp` is a tiny program using the legacy `readANNFile`. It was NOT compiled by me.
Build it against `uclv_learning_lib_legacy` and TooN (find TooN with `find / -name TooN.h`), feed it the
same CSV as `tactile_train predict`, and diff the outputs (expected agreement about 1e-8).

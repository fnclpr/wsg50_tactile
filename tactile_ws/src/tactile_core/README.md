# tactile_core

Hardware-independent, ROS-independent core math library for the
Vanvitelli force/tactile sensor (Costanzo et al., *Sensors* 2019, 19, 966).

This is **Step 1** of the project roadmap: every function here is a
direct, line-by-line-traceable port of a MATLAB function from
`matlab_calibration_gui/gui_lib/`, with the exact source function named
in each module's docstring. No ROS2, no hardware, no Docker required to
develop or test this package.

## Install (editable, with test dependencies)

```bash
cd tactile_ws/src/tactile_core
pip install -e ".[dev]"
```

## Run the tests

```bash
pytest -v
```

Expected: **45 passed** (26 from Step 1's `processing/` math ports +
7 from Step 8's `calibration/dataset.py` + 5 from Step 9's
`calibration/binning.py` + 7 from Step 10's `calibration/decimation.py`).
Note: 2 of the Step 8 tests require a real `h5py` install (already in
`docker/requirements.txt` for the dev container) — if you're running
this outside the container without h5py installed, those 2 will fail
at import/collection with `ModuleNotFoundError`, not because of a real
bug; `pip install h5py` resolves it.

## What's ported so far

| Module | MATLAB source | Paper equation |
|---|---|---|
| `processing/centroid.py` | `compute_centroid.m` | Eq. (3)-(4) |
| `processing/geometry.py` | `compute_contact_transform.m`, `compute_zone_central_transforms.m` | Eq. (5)-(7) |
| `processing/limit_surface.py` | `compute_max_ft.m`, `compute_max_taun.m`, `compute_wrench_plot_point.m` | Eq. (1)-(2) |
| `processing/zoning.py` | `find_interval.m`, `find_geometric_zone.m`, `compute_num_zones.m` | Section 3.1 stratification |
| `processing/wrench_transform.py` | `transform_wrench.m` | Eq. (8)-(9) |

## Step 8: calibration dataset structure

`calibration/dataset.py` is the Python-native equivalent of
`struct_projectData.m`/`struct_calib_data.m`: `FingerInfo` +
`CalibConfig` dataclasses (matching the legacy fields and defaults
exactly, including the `alpha`/`z_coord` derived-constant formulas),
plus `ProjectData`, a flat sample table (one row per calibration
sample) saved as one HDF5 file (numeric arrays) + one YAML sidecar
(metadata), rather than MATLAB's pre-binned `{zone, fn}` cell-array
grid.

**Why flat, not pre-binned** (a deliberate deviation from the legacy
*storage* layout, not from legacy *usage*): `zone_index`/`fn_index`
are derived quantities, computed after the fact from each sample's
centroid and normal force. A flat table lets you re-derive bins on
demand (`ProjectData.samples_in_bin(zone, fn)`) without reshaping
anything if `zone_radius_intervals` or `fn_intervals` ever changes —
and it actually matches how the legacy pipeline *consumes* the data
anyway: `mergeCalibData.m` flattens every `{zone,fn}` cell into one
matrix before decimation/training ever touches it. See the full
rationale in `dataset.py`'s module docstring.

## Step 9: fn-bin sentinel helper

`calibration/binning.py` adds `compute_fn_index(fz, fn_intervals)`, a
thin wrapper around `processing.zoning.find_interval` that converts
its NaN convention to the -1 sentinel used everywhere else
(`ProjectData.zone_index`, `tactile_msgs/TactileProcessed`). This is
the only new math in Step 9 — used by `tactile_gui`'s calibration
acquisition GUI, but kept here (not in the GUI package) so it stays
unit-testable without PySide6/rclpy installed.

## Step 10: bubble decimation (Eq. 10-13)

`calibration/decimation.py` ports the paper's published bubble
decimation algorithm verbatim (the literal MATLAB listing in Section
3.2 is quoted in full in the module docstring). `bubble_decimation`
operates on a plain `(N, D)` array; `decimate_project_data` applies it
independently within each `(zone_index, fn_index)` bin of a
`ProjectData`, per the paper's own guidance to decimate per-bin rather
than globally.

**Genuine gap, flagged rather than guessed at**: the legacy
`sun_finger_decim.m` calls a `sun_train_decim(...)` function with
input/target normalization options that was never provided to me --
only the outer per-zone/per-fn loop exists in the material I have.
This module implements exactly the paper's published, unnormalized
algorithm; if `sun_train_decim.m`'s real normalization scheme
surfaces later, it should be added as an explicit pre-processing step,
not silently folded in here.

## Important note found while writing these tests

`compute_contact_transform`'s rotation construction (`sc_x_cont`,
`sc_y_cont`) projects the sensor's x/y axes onto the tangent plane and
normalizes each independently, but does **not** re-orthogonalize them
against each other. Each is exactly unit-norm and exactly orthogonal to
the surface normal `n_hat`, but `sc_x_cont . sc_y_cont` is only
*approximately* zero, and the approximation degrades as the centroid
offset grows relative to the sphere radius R. This is a genuine
property of the **original MATLAB algorithm**, not a porting bug — see
the "IMPORTANT" note in `geometry.py` and `test_geometry.py`. Do not
"fix" this by orthogonalizing; that would make this implementation
numerically diverge from the legacy system.

## Known open items (not yet resolved, tracked from the project analysis doc)

- Taxel channel ordering (index 0..24 -> physical row/col) is assumed
  row-major per `struct_finger_info.m`'s coordinate arrays, but is not
  independently verified against sensor firmware.
- `find_interval` / `find_geometric_zone` intentionally still return
  MATLAB's 1-indexed convention (or NaN). A 0-indexed wrapper will be
  added when this library is consumed by the ROS2 processing nodes.
- `mu`, `alpha`, `gamma` (limit-surface constants) are per-sensor
  calibration values, not constants — nothing in this package
  hardcodes them; every function takes them as explicit arguments.

# tactile_msgs

New ROS2 interfaces for the tactile sensor system — **only** the ones
that don't already exist in the legacy repo.

## Why this package exists (and why it's small)

Per the project rule "don't rewrite existing functionality
unnecessarily" (Section 3/36 of the project plan), the following
interfaces are **intentionally reused as-is, not redefined here**:

| Interface | Where it already lives | Used for |
|---|---|---|
| `Tactile.msg`, `TactileStamped.msg` | `uclv_tactile_interfaces` | Raw/debiased 25-taxel voltage frames |
| `ComputeBias.action` | `uclv_tactile_interfaces` | Bias/debias action server |
| `Float64Stamped.msg` | `uclv_ros2_interfaces` | Finger-distance topic (`combine_wrench_node`) |
| `geometry_msgs/WrenchStamped` | ROS2 core | Per-finger and grasp wrench output |

`tactile_msgs` adds only what genuinely doesn't exist anywhere yet:

| Message | Purpose |
|---|---|
| `CalibrationStatus.msg` | Calibration validity/metrics, consumed by both GUIs and the (future) force controller's safety check |
| `TactileProcessed.msg` | Bundles `tactile_core.processing` output (centroid, zone, limit-surface point) for the monitor GUI |

## Build

From the workspace root (`/workspace` inside the dev container):

```bash
colcon build --packages-select tactile_msgs --symlink-install
source install/setup.bash
```

## Verify

```bash
ros2 interface show tactile_msgs/msg/CalibrationStatus
ros2 interface show tactile_msgs/msg/TactileProcessed
```

## Note on `tactile_core` coexisting in `src/`

`tactile_core` (Step 1) lives in `src/tactile_core` alongside this
package but is **not** a ROS2/colcon package — it has no `package.xml`.
A `COLCON_IGNORE` file was added to `src/tactile_core/` in this step so
`colcon build` (run with no `--packages-select` filter) never tries to
mistake its `pyproject.toml` for a buildable package.

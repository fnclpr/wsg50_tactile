# tactile_ws

Force/tactile sensor + WSG50-110 system, built on top of Costanzo et
al., "Design and Calibration of a Force/Tactile Sensor for Dexterous
Manipulation" (*Sensors* 2019, 19, 966). See `00_PROJECT_ANALYSIS.md`
(delivered separately) for the full scientific/legacy-code analysis.

## Layout

```
tactile_ws/
├── docker/              # dev container (Step 2)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   └── requirements.txt
├── src/
│   ├── tactile_core/    # hardware/ROS-free math + calibration dataset (Steps 1, 8)
│   ├── tactile_msgs/    # new ROS2 interfaces (Step 3)
│   ├── uclv_tactile_sensor/   # ported sensor driver (Step 4)
│   │   ├── uclv_tactile_interfaces/
│   │   └── uclv_tactile_driver/
│   ├── tactile_processing/    # centroid + zone ROS2 node (Step 6)
│   └── tactile_gui/           # minimal monitor GUI (Step 7)
├── tools/               # hardware-independent test utilities (Step 4/5/6)
│   ├── fake_tactile_sensor.py
│   ├── verify_tactile_stream.py
│   ├── verify_debias_stream.py
│   └── verify_tactile_processed.py
├── tactile_ws.repos     # external (non-vendored) dependency, e.g. `serial`
├── calibration/         # exported calibration files (git-ignored contents)
└── data/                # recorded datasets / rosbags (git-ignored contents)
```

Future steps will add `src/tactile_wrench`, `src/wsg50_driver`,
`src/tactile_calibration`, `src/tactile_gui`, `src/tactile_bringup` as
ROS2 (ament) packages.

## Development workflow (Docker)

Everything from Step 2 onward runs inside the dev container — you do
**not** need ROS2 or any Python packages installed on your host, only
Docker itself.

### One-time setup (per host reboot, for GUI passthrough)

```bash
xhost +local:docker
```

This allows the container to draw windows on your host's X11 display.
Harmless on a local dev machine; do not run this on a shared/exposed
machine without understanding the access it grants.

### Build the image

```bash
cd tactile_ws/docker
docker compose build
```

### Start a shell in the container

```bash
docker compose run --rm tactile_dev bash
```

You land in `/workspace`, which is your `tactile_ws/` directory,
live-mounted. Anything you edit on the host is immediately visible
here, and vice versa.

### Run the Step 1 tests inside the container

```bash
pytest src/tactile_core/tests -v
```

### Verify ROS2 is alive

```bash
ros2 topic list
ros2 doctor
```

### Verify the GUI stack can talk to your display

```bash
python3 -c "from PySide6.QtWidgets import QApplication, QLabel; import sys; \
app = QApplication(sys.argv); w = QLabel('tactile_ws GUI test OK'); w.show(); \
print('platform:', app.platformName()); app.exec()"
```

A small window titled with your label should appear on your host
screen; close it to return to the shell.

## Known issue: pytest version pin

`docker/requirements.txt` pins `pytest<8`. ROS2 Jazzy's
`ros-dev-tools` (installed via apt in the Dockerfile) pulls in
`python3-launch-testing`, which registers a pytest plugin built
against pytest 7.x's plugin hookspec. pytest 8 changed that hookspec
(`pytest_pycollect_makemodule`'s `path` argument became
`collection_path`), so any pytest 8.x install fails immediately with
`PluginValidationError` as soon as it tries to load the
`launch_testing` plugin — even for tests that have nothing to do with
ROS2. Discovered empirically during Step 2. Do not remove this pin
without first checking whether a newer ROS2 Jazzy release has updated
`launch_testing` for pytest 8 compatibility.

## Step 4: tactile sensor driver (ported, hardware-free tested)

`src/uclv_tactile_sensor/` is a faithful port of the existing, working
ROS2 sensor driver (`uclv_tactile_interfaces` + `uclv_tactile_driver`).
It depends on an external `serial` C++ library that isn't vendored —
fetch it before building:

```bash
cd /workspace
vcs import src < tactile_ws.repos
```

(`Vanvitelli-Robotics/serial.git` — confirmed working end-to-end in Step 4.)

Build and test **without any physical hardware**, using the fake
sensor emulator in `tools/`:

```bash
colcon build --packages-select uclv_tactile_interfaces uclv_tactile_driver --symlink-install
source install/setup.bash

# terminal 1
python3 tools/fake_tactile_sensor.py --rows 5 --cols 5
# copy the printed PTY path, e.g. /dev/pts/3

# terminal 2 (same container: docker compose run --rm tactile_dev bash)
source /workspace/install/setup.bash
ros2 run uclv_tactile_driver read_tactile_serial --ros-args \
    -p serial_port:=/dev/pts/3 -p baud_rate:=115200 -p rows:=5 -p cols:=5

# terminal 3
source /workspace/install/setup.bash
python3 tools/verify_tactile_stream.py --topic /tactile_voltage/raw --rows 5 --cols 5
```

Expected: `verify_tactile_stream.py` exits 0 and prints "All 25 taxel
values match expected voltages. PASS." See `tools/README.md` for
details, including a known-harmless `setserial` warning you'll see on
the PTY.

## Step 5: bias/debias action server (hardware-free tested)

`remove_bias` (already built since Step 4) subscribes to the raw
topic, computes a bias by averaging N samples, and republishes
debiased data. Test it against the same fake sensor from Step 4 — its
determinism (identical output every request) makes the expected result
trivial: a correctly-computed bias must drive every debiased sample to
~0.0.

**Read `tools/README.md`'s "two things to know" before running this**
— `num_voltages` defaults to 12 (must override to 25), and the
`ComputeBias` action never actually returns the bias values it
computed (known legacy limitation, not a test bug).

Keep terminals 1 and 2 from Step 4 running (fake sensor +
`read_tactile_serial`), then add:

```bash
# terminal 4 (docker exec -it tactile_dev bash; source both setup.bash files)
ros2 run uclv_tactile_driver remove_bias --ros-args \
    -p in_voltage_topic:=tactile_voltage/raw \
    -p out_voltage_topic:=tactile_voltage/rect \
    -p num_voltages:=25 \
    -p default_num_samples:=30

# terminal 5
python3 tools/verify_debias_stream.py --topic /tactile_voltage/rect --rows 5 --cols 5
```

Expected: terminal 5 prints "All 25 debiased values are ~0.0 ...
PASS." and exits 0.

Optional secondary check — confirm the action interface itself works
(expect `success: true`, `bias: []` — the empty array is the known
limitation above, not a failure):

```bash
ros2 action send_goal /tactile_voltage/action_compute_bias \
    uclv_tactile_interfaces/action/ComputeBias "{num_samples: 30}"
```

## Step 6: centroid + zone ROS2 node (hardware-free tested)

`tactile_processing` subscribes to tactile data and publishes
`tactile_msgs/TactileProcessed` (centroid + geometric zone), calling
directly into `tactile_core.processing` (Step 1) rather than
reimplementing any math. `limit_surface_point` is intentionally always
`[0.0, 0.0, 0.0]` — it needs a wrench estimate that doesn't exist until
Step 12; this is documented, not an oversight.

Build it:

```bash
colcon build --packages-select tactile_processing --symlink-install
source install/setup.bash
```

Test against the fake sensor from Step 4 (terminals 1 and 2 from that
step should still be running). For a non-degenerate centroid, point
this node at the **raw** topic, not the all-zero debiased one from
Step 5:

```bash
# terminal 6
ros2 run tactile_processing tactile_processing_node --ros-args \
    -p in_topic:=tactile_voltage/raw \
    -p out_topic:=tactile_processed

# terminal 7
python3 tools/verify_tactile_processed.py --topic /tactile_processed --rows 5 --cols 5
```

Expected: terminal 7 prints the independently-computed expected values
(`centroid=(0.000583, -0.002917)`, `zone_index=5`), then confirms the
subscribed message matches and prints "... PASS." Terminal 6 will also
print a one-time warning about `limit_surface_point` not being
populated yet — expected, not an error.

## Step 7: minimal monitor GUI (visual, hardware-free tested)

`tactile_gui`'s `monitor_gui` is the first visual proof that Steps 1-6
work together: a live 5x5 heatmap of raw voltages with the centroid
overlaid as a dot, reading directly off the same topics
`tactile_processing_node` publishes.

Build it:

```bash
colcon build --packages-select tactile_gui --symlink-install
source install/setup.bash
```

Requires the GUI passthrough from Step 2 (`xhost +local:docker` on the
host, `$DISPLAY` set). Keep terminals 1/2 (fake sensor +
`read_tactile_serial`) and 6 (`tactile_processing_node`, pointed at
`tactile_voltage/raw` as in Step 6) running, then:

```bash
# terminal 8
ros2 run tactile_gui monitor_gui --ros-args \
    -p voltage_topic:=tactile_voltage/raw \
    -p processed_topic:=tactile_processed
```

Expected: a window titled "tactile_ws -- monitor GUI (Step 7)" opens
showing a 5x5 grid colored by voltage (redder = higher, taxel 0 at
top-left ~0V through taxel 24 at bottom-right ~1.93V, per the fake
sensor's fixed ramp), a blue dot near the lower-middle of the grid
(matching the Step 6 centroid ≈ (0.00058, -0.00292)), and a status
line reading `centroid: (0.0006, -0.0029) m   zone: 5`.

The coordinate mapping (physical meters -> pixel position) was
verified independently against all 4 sensor-corner cases, the
sensor-center case, and the exact Step 6 centroid value before this
was shipped -- see project history for the verification script.

## Step 9: calibration acquisition GUI (visual, hardware-free tested)

`tactile_gui`'s `calibration_gui` reuses Step 7's `HeatmapWidget`
directly and adds: a manual wrench-entry panel (there is no reference
F/T sensor ROS2 driver yet -- documented scope limitation, not an
oversight), sample acceptance with zone/fn-bin validation, and
save-to-disk via Step 8's `ProjectData`. Pose is stored as an identity
placeholder for the same reason.

The only new math (`compute_fn_index`, mapping fz to its bin with the
same -1 sentinel convention as everything else) lives in
`tactile_core.calibration.binning`, unit-tested independently of any
GUI/ROS2 code — see `src/tactile_core/README.md`.

Build it:

```bash
colcon build --packages-select tactile_gui --symlink-install
source install/setup.bash
```

Test against the same fake-sensor setup as Steps 6/7 (terminals 1, 2,
6 running):

```bash
# terminal 9
ros2 run tactile_gui calibration_gui --ros-args \
    -p in_topic:=tactile_voltage/raw \
    -p processed_topic:=tactile_processed \
    -p finger_id:=F999_dry_run
```

Expected: a window opens with the same heatmap as Step 7 plus, on the
right, an orange "MANUAL WRENCH ENTRY" warning, 6 spin boxes, and
status/fn-bin/count labels. With the default fz=0.0, "fn bin" should
read `1` (matches `compute_fn_index(0.0, [0,2,4,6,8.5]) == 1`, the
left-edge special case) and "Accept Sample" should be enabled (zone=5
from Step 6/7's fixed fake-sensor centroid, fn=1, both valid). Click
"Accept Sample" a few times — the counter should increment each time.
Click "Save Project...", pick a path, and confirm `<path>.h5` and
`<path>.yaml` appear in `calibration/`.

## Step 10: bubble decimation (Eq. 10-13, library-only, no GUI/ROS2 needed)

`tactile_core.calibration.decimation` ports the paper's published
bubble decimation algorithm verbatim, plus a wrapper
(`decimate_project_data`) applying it independently within each
(zone, fn) bin of a `ProjectData` (Step 8). This step is pure library
code -- no ROS2 nodes, no GUI, no terminals to launch. Confirm it with
the test suite:

```bash
cd /workspace/src/tactile_core
pytest -v
```

Expected: **45 passed** (up from 38). See `src/tactile_core/README.md`
for a flagged, genuine gap: the legacy `sun_train_decim.m` (which the
outer `sun_finger_decim.m` loop calls) includes input/target
normalization options that were never provided in the source material
-- this step implements exactly the paper's published, unnormalized
algorithm, not a guess at that missing normalization.

## Rebuilding

Only rebuild the image when you change `docker/Dockerfile` or
`docker/requirements.txt`:

```bash
docker compose build --no-cache   # --no-cache only if apt/pip state seems stale
```

Everyday code changes (Python, launch files, etc.) never require a
rebuild — the bind mount handles it.

# tools/

Hardware-independent test utilities (Section 22 of the project plan).

## `fake_tactile_sensor.py`

Emulates the real sensor's serial protocol over a pseudo-terminal
(PTY), so `read_tactile_serial` can be tested without any physical
hardware. Prints the PTY device path to use as the node's
`serial_port` parameter, and the exact expected voltages it will
produce (25 distinct, predictable values — taxel `i` gets raw ADC
value `min(i*100, 4095)`).

Verified (see project history) with:
- an offline simulation of the node's C++ conversion formula against
  the generated payload bytes,
- an actual OS-level PTY round-trip test (open the slave path, send
  the request byte, read the response, decode it) — this is what
  caught a real bug: `pty.openpty()` defaults to canonical+echo mode
  (like an interactive terminal), which corrupts binary payloads. The
  script now explicitly sets both ends to raw mode (`tty.setraw`),
  matching what `socat ...,raw,echo=0` does for the same reason,
- 20 consecutive request/response cycles, matching the real node's
  continuous acquisition loop.

```bash
python3 tools/fake_tactile_sensor.py --rows 5 --cols 5
```

## `verify_tactile_stream.py`

An `rclpy` node that subscribes to the driver's output topic, waits
for one message, and checks every taxel value against the exact
expected voltages `fake_tactile_sensor.py` computed (imported directly
from it, so the two scripts can never silently drift out of sync).
Exits 0 on match, 1 otherwise — a real automated pass/fail test, not
"eyeball `ros2 topic echo`".

```bash
python3 tools/verify_tactile_stream.py --topic /tactile_voltage/raw --rows 5 --cols 5
```

## `verify_debias_stream.py`

Automated Step 5 check for `remove_bias`. Because `fake_tactile_sensor.py`
is fully deterministic, a correctly-computed bias makes every debiased
sample come out ~0.0 for all taxels — a clean, hand-derivable expected
result requiring no new math.

```bash
python3 tools/verify_debias_stream.py --topic /tactile_voltage/rect --rows 5 --cols 5
```

**Two things to know about `remove_bias_node.cpp` before running it**
(found by reading the source closely, not by trial and error):

1. `num_voltages` parameter defaults to **12, not 25** — you must pass
   `-p num_voltages:=25` explicitly for a 5x5 sensor, or taxels 12-24
   will silently stay un-debiased. This script names the exact failing
   taxel indices, so this mistake is self-diagnosing if you forget.
2. The `ComputeBias` **action never populates its `bias` result field**
   — `executeComputeBiasCB` sets `success` but never copies the node's
   internally-computed bias vector into the action result before
   calling `goal_handle->succeed()`. If you manually trigger the
   action with `ros2 action send_goal`, expect `success: true` but
   `bias: []` (empty) — that's a known legacy limitation, not a bug in
   this test.

## `verify_tactile_processed.py`

Automated Step 6 check for `tactile_processing_node`. Computes the
expected centroid + zone directly from `tactile_core.processing`
(already unit-tested in Step 1) on the same known raw voltages
`fake_tactile_sensor.py` produces, then checks the node's published
`tactile_processed` message matches exactly. This validates the ROS
*wiring* (topic, parameters, message field mapping) — a different
concern from Step 1's math unit tests.

Point the node at `tactile_voltage/raw` (not the debiased
`tactile_voltage/rect`, which is all ~0.0 per the Step 5 setup — valid
but a degenerate "no contact" case) to get a non-trivial centroid:

```bash
python3 tools/verify_tactile_processed.py --topic /tactile_processed --rows 5 --cols 5
```

Expected values for the default 5x5/0.007m-pitch setup: centroid ≈
`(0.000583, -0.002917)` m, `zone_index = 5`.

**`limit_surface_point` is intentionally always `[0.0, 0.0, 0.0]`** in
this node's output — it requires a wrench estimate that doesn't exist
until Step 12. Don't be alarmed that this test never checks it.

## Known non-fatal warning you'll see

`read_tactile_serial_node.cpp` runs `setserial <port> low_latency`
before opening the port. `setserial` only works on real UART devices,
so against a PTY it prints something like:

```
Setting low_latency for /dev/pts/3
Cannot get serial info: Inappropriate ioctl for device
Setting low_latency for /dev/pts/3 result:1
```

This is expected and harmless when testing against the fake sensor —
the node does not check this command's exit code before continuing.
It will behave normally on real hardware.

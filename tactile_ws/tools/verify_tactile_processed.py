#!/usr/bin/env python3
"""
Automated Step 6 verification.

Subscribes to `tactile_processed` and checks the published centroid +
zone_index against the SAME tactile_core.processing functions the node
itself calls -- already unit-tested independently in Step 1 with 26
hand-derived reference cases.

This is deliberate, not circular: Step 1's tests validate that the MATH
is correct in isolation (no ROS involved at all). This test validates
that the ROS WIRING is correct -- the right topic is subscribed, the
right taxel-coordinate convention/parameters are used, and the result
is mapped into the right message fields. That is a different, real
risk (parameter typos, coordinate-convention mismatches, message field
mix-ups) that a pure math unit test cannot catch.

For a non-degenerate check (a real off-center centroid, not the [0,0]
"no contact" case), point tactile_processing_node's `in_topic`
parameter at tactile_voltage/raw for THIS test -- not the debiased
tactile_voltage/rect, which is all ~0.0 given the Step 5 test setup (a
valid but uninteresting all-zero case). See README for the exact
launch command.

Usage:
    python3 tools/verify_tactile_processed.py --topic /tactile_processed --rows 5 --cols 5
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fake_tactile_sensor import build_payload  # noqa: E402

from tactile_core.processing.centroid import compute_centroid  # noqa: E402
from tactile_core.processing.zoning import find_geometric_zone  # noqa: E402

import rclpy  # noqa: E402
from rclpy.node import Node  # noqa: E402
from tactile_msgs.msg import TactileProcessed  # noqa: E402

# Must match tactile_processing_node.py's defaults exactly.
_DEFAULT_ZONE_ANGLE_BOUND_LINES = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]
_DEFAULT_ZONE_RADIUS_INTERVALS = [0.0015, 0.0045, 0.01]
_GRID_PATTERN = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])


def compute_expected(pitch: float, rows: int, cols: int) -> tuple[np.ndarray, int]:
    num_taxels = rows * cols
    _, voltages = build_payload(num_taxels)
    voltages = np.array(voltages)

    row = _GRID_PATTERN * pitch
    col = _GRID_PATTERN[::-1] * pitch
    taxels_x = np.tile(row, (5, 1))
    taxels_y = np.tile(col.reshape(5, 1), (1, 5))

    centroid = compute_centroid(voltages, taxels_x, taxels_y)
    zone = find_geometric_zone(centroid, _DEFAULT_ZONE_ANGLE_BOUND_LINES, _DEFAULT_ZONE_RADIUS_INTERVALS)
    zone_index = -1 if math.isnan(zone) else int(zone)
    return centroid, zone_index


class ProcessedVerifierNode(Node):
    def __init__(self, topic: str, expected_centroid: np.ndarray, expected_zone: int, tolerance: float):
        super().__init__("verify_tactile_processed")
        self._expected_centroid = expected_centroid
        self._expected_zone = expected_zone
        self._tolerance = tolerance
        self.passed: "bool | None" = None
        self.sub = self.create_subscription(TactileProcessed, topic, self._cb, 10)
        self.get_logger().info(f"Waiting for one message on {topic} ...")

    def _cb(self, msg: TactileProcessed) -> None:
        got_centroid = (msg.centroid.x, msg.centroid.y)
        ok_centroid = all(
            abs(got - exp) < self._tolerance for got, exp in zip(got_centroid, self._expected_centroid)
        )
        ok_zone = msg.zone_index == self._expected_zone

        if ok_centroid and ok_zone:
            self.get_logger().info(
                f"centroid={got_centroid}, zone_index={msg.zone_index} -- matches expected "
                f"centroid={tuple(self._expected_centroid)}, zone={self._expected_zone}. PASS."
            )
            self.passed = True
        else:
            self.get_logger().error(
                f"MISMATCH: got centroid={got_centroid}, zone_index={msg.zone_index}; "
                f"expected centroid={tuple(self._expected_centroid)}, zone={self._expected_zone}"
            )
            self.passed = False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", default="/tactile_processed")
    parser.add_argument("--rows", type=int, default=5)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--pitch", type=float, default=0.007)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    expected_centroid, expected_zone = compute_expected(args.pitch, args.rows, args.cols)
    print(f"Expected (computed directly from tactile_core, no ROS involved): "
          f"centroid={tuple(expected_centroid)}, zone_index={expected_zone}")

    rclpy.init()
    node = ProcessedVerifierNode(args.topic, expected_centroid, expected_zone, args.tolerance)

    start = time.monotonic()
    while node.passed is None and (time.monotonic() - start) < args.timeout:
        rclpy.spin_once(node, timeout_sec=0.1)

    result = node.passed
    node.destroy_node()
    rclpy.shutdown()

    if result is None:
        print(f"FAIL: no message received on {args.topic} within {args.timeout}s")
        return 1

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())

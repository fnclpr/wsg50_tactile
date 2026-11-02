#!/usr/bin/env python3
"""
Automated Step 4 verification.

Subscribes to the topic `read_tactile_serial` publishes on, waits for
one message, and checks its 25 (or rows*cols) voltage values against
the exact expected values computed by fake_tactile_sensor.py's
raw12_to_expected_voltage() -- the SAME function used to build the fake
payload, so there is no independent rounding to drift out of sync.

This turns "look at ros2 topic echo and eyeball it" into a real
pass/fail test, per the project's hardware-independent testing
philosophy (Section 22 of the project plan).

Usage (inside the container, ROS2 environment already sourced):
    python3 tools/verify_tactile_stream.py --topic /tactile_voltage/raw --rows 5 --cols 5

Exit code 0 = PASS, 1 = FAIL or timeout.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Import the exact same expected-value computation the fake sensor uses,
# so this test can never silently drift out of sync with it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fake_tactile_sensor import build_payload  # noqa: E402

import rclpy  # noqa: E402
from rclpy.node import Node  # noqa: E402
from uclv_tactile_interfaces.msg import TactileStamped  # noqa: E402


class VerifierNode(Node):
    def __init__(self, topic: str, num_taxels: int, expected: list[float], tolerance: float):
        super().__init__("verify_tactile_stream")
        self._expected = expected
        self._num_taxels = num_taxels
        self._tolerance = tolerance
        self.passed: "bool | None" = None
        self.sub = self.create_subscription(TactileStamped, topic, self._cb, 10)
        self.get_logger().info(f"Waiting for one message on {topic} ...")

    def _cb(self, msg: TactileStamped) -> None:
        data = list(msg.tactile.data)
        if len(data) != self._num_taxels:
            self.get_logger().error(f"Expected {self._num_taxels} values, got {len(data)}")
            self.passed = False
            return

        failures = [
            (i, got, exp)
            for i, (got, exp) in enumerate(zip(data, self._expected))
            if abs(got - exp) > self._tolerance
        ]

        if failures:
            self.get_logger().error(f"{len(failures)}/{self._num_taxels} taxels mismatched:")
            for i, got, exp in failures[:10]:
                self.get_logger().error(f"  taxel {i}: got {got:.6f}, expected {exp:.6f}")
            self.passed = False
        else:
            self.get_logger().info(f"All {self._num_taxels} taxel values match expected voltages. PASS.")
            self.passed = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", default="/tactile_voltage/raw")
    parser.add_argument("--rows", type=int, default=5)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    num_taxels = args.rows * args.cols
    _, expected_voltages = build_payload(num_taxels)

    rclpy.init()
    node = VerifierNode(args.topic, num_taxels, expected_voltages, args.tolerance)

    start = time.monotonic()
    while node.passed is None and (time.monotonic() - start) < args.timeout:
        rclpy.spin_once(node, timeout_sec=0.1)

    result = node.passed
    node.destroy_node()
    rclpy.shutdown()

    if result is None:
        print(
            f"FAIL: no message received on {args.topic} within {args.timeout}s "
            f"(is read_tactile_serial running and publishing on this topic?)"
        )
        return 1

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())

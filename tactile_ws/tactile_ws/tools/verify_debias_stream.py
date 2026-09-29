#!/usr/bin/env python3
"""
Automated Step 5 verification.

Subscribes to remove_bias's debiased output topic and checks that
every taxel value is ~0.0. This works BECAUSE fake_tactile_sensor.py
is fully deterministic (identical payload on every request): if the
bias computation correctly averages N identical samples, the computed
bias equals those exact raw values, so every subsequent debiased
sample must be (raw - bias) = 0 for all taxels, up to float32
rounding.

If specific taxels consistently fail while others pass, check whether
you passed `-p num_voltages:=25` when launching remove_bias -- its
default is 12, and forgetting the override leaves taxels 12-24
un-debiased (still raw, not near zero). This script will name exactly
which taxel indices failed, which is the fastest way to spot that
mistake.

Usage (inside the container, ROS2 environment already sourced):
    python3 tools/verify_debias_stream.py --topic /tactile_voltage/rect --rows 5 --cols 5
"""
from __future__ import annotations

import argparse
import sys
import time

import rclpy
from rclpy.node import Node
from uclv_tactile_interfaces.msg import TactileStamped


class DebiasVerifierNode(Node):
    def __init__(self, topic: str, num_taxels: int, tolerance: float):
        super().__init__("verify_debias_stream")
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

        failures = [(i, v) for i, v in enumerate(data) if abs(v) > self._tolerance]

        if failures:
            self.get_logger().error(f"{len(failures)}/{self._num_taxels} taxels NOT near zero:")
            for i, v in failures[:10]:
                self.get_logger().error(f"  taxel {i}: {v:.6f} (expected ~0.0)")
            if all(i >= 12 for i, _ in failures):
                self.get_logger().error(
                    "All failing taxels are index >= 12 -- did you forget "
                    "'-p num_voltages:=25' when launching remove_bias? "
                    "(default is 12, see tools/README.md)"
                )
            self.passed = False
        else:
            self.get_logger().info(
                f"All {self._num_taxels} debiased values are ~0.0 "
                f"(within {self._tolerance}). PASS."
            )
            self.passed = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", default="/tactile_voltage/rect")
    parser.add_argument("--rows", type=int, default=5)
    parser.add_argument("--cols", type=int, default=5)
    parser.add_argument("--tolerance", type=float, default=1e-3)
    parser.add_argument("--timeout", type=float, default=20.0,
                         help="generous timeout: remove_bias blocks at startup "
                              "computing its initial bias before it publishes anything")
    args = parser.parse_args()

    num_taxels = args.rows * args.cols

    rclpy.init()
    node = DebiasVerifierNode(args.topic, num_taxels, args.tolerance)

    start = time.monotonic()
    while node.passed is None and (time.monotonic() - start) < args.timeout:
        rclpy.spin_once(node, timeout_sec=0.1)

    result = node.passed
    node.destroy_node()
    rclpy.shutdown()

    if result is None:
        print(
            f"FAIL: no message received on {args.topic} within {args.timeout}s "
            f"(is remove_bias running? has it finished its initial bias computation yet?)"
        )
        return 1

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())

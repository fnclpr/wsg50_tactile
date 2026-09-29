"""
Bridges tactile_core.processing (Step 1, hardware/ROS-free) into the
ROS2 graph. Subscribes to debiased tactile data
(uclv_tactile_interfaces/msg/TactileStamped) and publishes
tactile_msgs/msg/TactileProcessed (centroid + geometric zone).

Deliberately does NOT reimplement any math here -- every numeric
computation is a call into tactile_core.processing, which already has
26 hand-derived-reference unit tests (Step 1). This node's only job is
ROS-level glue: parameter handling, subscribing/publishing, and
mapping between numpy arrays and ROS2 message fields.

limit_surface_point is NOT populated (see package.xml and README) --
it requires a wrench estimate that doesn't exist until Step 12.
"""
from __future__ import annotations

import math

import numpy as np
import rclpy
from geometry_msgs.msg import Point
from rcl_interfaces.msg import ParameterDescriptor, ParameterType
from rclpy.node import Node
from uclv_tactile_interfaces.msg import TactileStamped

from tactile_core.processing.centroid import compute_centroid
from tactile_core.processing.zoning import find_geometric_zone

from tactile_msgs.msg import TactileProcessed

# Matches struct_finger_info.m's default taxel layout: a 5x5 grid where
# each axis is [-1, -0.5, 0, 0.5, 1] scaled by a single pitch value.
_GRID_PATTERN = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])

# Matches create_empty_project.m's defaults.
_DEFAULT_ZONE_ANGLE_BOUND_LINES = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]
_DEFAULT_ZONE_RADIUS_INTERVALS = [0.0015, 0.0045, 0.01]


class TactileProcessingNode(Node):
    def __init__(self) -> None:
        super().__init__("tactile_processing_node")

        self.declare_parameter("in_topic", "tactile_voltage/rect")
        self.declare_parameter("out_topic", "tactile_processed")
        self.declare_parameter("taxel_pitch", 0.007)
        self.declare_parameter(
            "broken_cells",
            [],
            ParameterDescriptor(type=ParameterType.PARAMETER_INTEGER_ARRAY),
        )
        self.declare_parameter("zone_angle_bound_lines", _DEFAULT_ZONE_ANGLE_BOUND_LINES)
        self.declare_parameter("zone_radius_intervals", _DEFAULT_ZONE_RADIUS_INTERVALS)

        in_topic = self.get_parameter("in_topic").value
        out_topic = self.get_parameter("out_topic").value
        pitch = float(self.get_parameter("taxel_pitch").value)
        broken_cells = list(self.get_parameter("broken_cells").value)
        self._broken_cells = broken_cells if broken_cells else None
        self._zone_angle_bound_lines = list(self.get_parameter("zone_angle_bound_lines").value)
        self._zone_radius_intervals = list(self.get_parameter("zone_radius_intervals").value)

        row = _GRID_PATTERN * pitch
        col = _GRID_PATTERN[::-1] * pitch  # [1, 0.5, 0, -0.5, -1] -- matches taxels_y_coords convention
        self._taxels_x = np.tile(row, (5, 1))
        self._taxels_y = np.tile(col.reshape(5, 1), (1, 5))

        self._sub = self.create_subscription(TactileStamped, in_topic, self._on_tactile, 10)
        self._pub = self.create_publisher(TactileProcessed, out_topic, 10)

        self.get_logger().info(
            f"tactile_processing_node: '{in_topic}' -> '{out_topic}' "
            f"(taxel_pitch={pitch}, broken_cells={self._broken_cells})"
        )
        self.get_logger().warn(
            "limit_surface_point is NOT populated yet -- it requires a wrench "
            "estimate that does not exist until Step 12 (ANN inference / "
            "combine_wrench). Always published as [0.0, 0.0, 0.0]; do not "
            "interpret it as real data."
        )

    def _on_tactile(self, msg: TactileStamped) -> None:
        voltages = np.asarray(msg.tactile.data, dtype=float)
        if voltages.size != 25:
            self.get_logger().error(
                f"expected 25 taxel values, got {voltages.size}; dropping this message"
            )
            return

        centroid = compute_centroid(
            voltages, self._taxels_x, self._taxels_y, broken_cells=self._broken_cells
        )
        zone = find_geometric_zone(
            centroid, self._zone_angle_bound_lines, self._zone_radius_intervals
        )
        zone_index = -1 if math.isnan(zone) else int(zone)

        out = TactileProcessed()
        out.header = msg.header
        out.centroid = Point(x=float(centroid[0]), y=float(centroid[1]), z=0.0)
        out.zone_index = zone_index
        out.limit_surface_point = [0.0, 0.0, 0.0]  # placeholder -- see Step 12
        self._pub.publish(out)


def main(args: "list[str] | None" = None) -> None:
    rclpy.init(args=args)
    node = TactileProcessingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

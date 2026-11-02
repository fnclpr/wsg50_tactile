"""
Minimal monitor GUI (Step 7): live 5x5 tactile heatmap + centroid dot.

Architecture note: rclpy spinning and the Qt event loop share the SAME
thread here, driven by a QTimer that periodically calls
rclpy.spin_once(). This is the simplest correct way to combine rclpy
and Qt in one process -- no cross-thread signal/slot machinery, no
GIL/race-condition risk -- and is entirely adequate for a monitoring
display (default ~30 Hz poll rate). Revisit only if a future GUI needs
lower end-to-end latency than this polling approach provides.

Coordinate convention (matches struct_finger_info.m / tactile_core):
row 0 = physical y = +pitch (top), row 4 = y = -pitch (bottom);
col 0 = physical x = -pitch (left), col 4 = x = +pitch (right).
"""
from __future__ import annotations

import sys

import rclpy
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from rclpy.node import Node
from uclv_tactile_interfaces.msg import TactileStamped

from tactile_msgs.msg import TactileProcessed


class TactileSubscriberNode(Node):
    """Pure data holder -- no processing, no publishing. Just keeps the
    latest received messages for the GUI to read on each timer tick."""

    def __init__(self) -> None:
        super().__init__("tactile_monitor_gui")

        self.declare_parameter("voltage_topic", "tactile_voltage/raw")
        self.declare_parameter("processed_topic", "tactile_processed")
        self.declare_parameter("taxel_pitch", 0.007)
        self.declare_parameter("voltage_max", 3.3)

        voltage_topic = self.get_parameter("voltage_topic").value
        processed_topic = self.get_parameter("processed_topic").value
        self.pitch = float(self.get_parameter("taxel_pitch").value)
        self.voltage_max = float(self.get_parameter("voltage_max").value)

        self.latest_voltages: "list[float] | None" = None
        self.latest_centroid: "tuple[float, float] | None" = None
        self.latest_zone: "int | None" = None

        self.create_subscription(TactileStamped, voltage_topic, self._on_voltages, 10)
        self.create_subscription(TactileProcessed, processed_topic, self._on_processed, 10)

        self.get_logger().info(
            f"tactile_monitor_gui: voltages<-'{voltage_topic}' processed<-'{processed_topic}' "
            f"(pitch={self.pitch}, voltage_max={self.voltage_max})"
        )

    def _on_voltages(self, msg: TactileStamped) -> None:
        self.latest_voltages = list(msg.tactile.data)

    def _on_processed(self, msg: TactileProcessed) -> None:
        self.latest_centroid = (msg.centroid.x, msg.centroid.y)
        self.latest_zone = msg.zone_index


class HeatmapWidget(QWidget):
    """Draws a 5x5 grid of taxel voltages plus a centroid dot overlay."""

    ROWS = 5
    COLS = 5

    def __init__(self, pitch: float, voltage_max: float, parent=None) -> None:
        super().__init__(parent)
        self._pitch = pitch
        self._voltage_max = voltage_max
        self.voltages: "list[float] | None" = None
        self.centroid: "tuple[float, float] | None" = None
        self.setMinimumSize(300, 300)

    def set_data(self, voltages: "list[float] | None", centroid: "tuple[float, float] | None") -> None:
        self.voltages = voltages
        self.centroid = centroid
        self.update()  # schedule a repaint

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override naming)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height()) - 20
        origin_x = (self.width() - side) / 2
        origin_y = (self.height() - side) / 2
        cell = side / self.COLS

        # --- heatmap cells ---
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.voltages is not None:
                    idx = row * self.COLS + col
                    v = self.voltages[idx] if idx < len(self.voltages) else 0.0
                else:
                    v = 0.0
                t = max(0.0, min(1.0, v / self._voltage_max)) if self._voltage_max > 0 else 0.0
                color = QColor(int(255 * t), int(255 * (1 - t)), 60)
                x = origin_x + col * cell
                y = origin_y + row * cell
                painter.fillRect(int(x), int(y), int(cell) - 1, int(cell) - 1, color)

        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(int(origin_x), int(origin_y), int(side), int(side))

        # --- centroid overlay ---
        # x in [-pitch, +pitch] -> pixel_x in [origin_x, origin_x+side] (left to right)
        # y in [-pitch, +pitch] -> pixel_y in [origin_y+side, origin_y] (bottom to top,
        #   since row 0 / top = physical +y, matching taxels_y_coords' convention)
        if self.centroid is not None and self._pitch > 0:
            cx, cy = self.centroid
            px = origin_x + side * (cx + self._pitch) / (2 * self._pitch)
            py = origin_y + side * (self._pitch - cy) / (2 * self._pitch)
            painter.setPen(QPen(Qt.blue, 2))
            painter.setBrush(Qt.blue)
            r = 6
            painter.drawEllipse(int(px - r), int(py - r), 2 * r, 2 * r)


class MonitorWindow(QMainWindow):
    def __init__(self, node: TactileSubscriberNode) -> None:
        super().__init__()
        self._node = node
        self.setWindowTitle("tactile_ws -- monitor GUI (Step 7)")

        central = QWidget()
        layout = QVBoxLayout(central)

        self.heatmap = HeatmapWidget(node.pitch, node.voltage_max)
        layout.addWidget(self.heatmap)

        self.status_label = QLabel("Waiting for data...")
        layout.addWidget(self.status_label)

        self.setCentralWidget(central)
        self.resize(400, 450)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(33)  # ~30 Hz

    def _on_timer(self) -> None:
        rclpy.spin_once(self._node, timeout_sec=0.0)
        self.heatmap.set_data(self._node.latest_voltages, self._node.latest_centroid)

        if self._node.latest_voltages is None:
            self.status_label.setText("Waiting for data...")
        else:
            zone = self._node.latest_zone
            centroid = self._node.latest_centroid
            zone_text = "n/a" if zone is None else str(zone)
            centroid_text = "n/a" if centroid is None else f"({centroid[0]:.4f}, {centroid[1]:.4f}) m"
            self.status_label.setText(f"centroid: {centroid_text}   zone: {zone_text}")


def main(args: "list[str] | None" = None) -> None:
    rclpy.init(args=args)
    node = TactileSubscriberNode()

    app = QApplication(sys.argv)
    window = MonitorWindow(node)
    window.show()

    exit_code = app.exec()

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

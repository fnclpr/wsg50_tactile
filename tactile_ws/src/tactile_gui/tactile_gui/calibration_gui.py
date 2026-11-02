"""
Calibration acquisition GUI (Step 9): drives an operator through
manual data collection for the calibration procedure described in
Costanzo et al., Sensors 2019, 19, 966, Section 3.1-3.3.

SCOPE LIMITATION (stated explicitly, not hidden): there is no ROS2
driver for the reference F/T sensor the paper uses to record
ground-truth wrenches during calibration (a Robotous RFT40 or
equivalent) -- that hardware integration is a separate, not-yet-scoped
gap. This step wires up everything ELSE (live centroid/zone display,
sample acceptance, zone/fn-bin counting, save-to-disk via
tactile_core.calibration.dataset.ProjectData) using a MANUAL WRENCH
ENTRY panel as a stand-in for that missing sensor. Swapping the manual
entry for a real subscription later requires no change to the rest of
this GUI's logic -- only _current_wrench() would change.

Pose is similarly not sourced from anything real yet (no WSG50 driver,
no external tracking) -- every sample is stored with an identity pose
placeholder, matching the honest-placeholder pattern already used for
TactileProcessed.limit_surface_point in Step 6.

All bin-assignment logic (fn_index) is delegated to
tactile_core.calibration.binning.compute_fn_index, which is unit
tested independently of this file (no PySide6/rclpy needed for those
tests) -- this module is deliberately thin ROS2/Qt glue only.
"""
from __future__ import annotations

import sys
import time

import rclpy
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from rclpy.node import Node
from uclv_tactile_interfaces.msg import TactileStamped

from tactile_core.calibration.binning import compute_fn_index
from tactile_core.calibration.dataset import CalibConfig, FingerInfo, ProjectData
from tactile_gui.monitor_gui import HeatmapWidget
from tactile_msgs.msg import TactileProcessed

IDENTITY_POSE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
WRENCH_FIELDS = ["fx", "fy", "fz", "taux", "tauy", "tauz"]


class CalibrationSubscriberNode(Node):
    """Same pure-data-holder pattern as monitor_gui.TactileSubscriberNode."""

    def __init__(self) -> None:
        super().__init__("tactile_calibration_gui")

        self.declare_parameter("in_topic", "tactile_voltage/rect")
        self.declare_parameter("processed_topic", "tactile_processed")
        self.declare_parameter("taxel_pitch", 0.007)
        self.declare_parameter("voltage_max", 3.3)
        self.declare_parameter("finger_id", "unknown")

        self.pitch = float(self.get_parameter("taxel_pitch").value)
        self.voltage_max = float(self.get_parameter("voltage_max").value)
        self.finger_id = self.get_parameter("finger_id").value

        in_topic = self.get_parameter("in_topic").value
        processed_topic = self.get_parameter("processed_topic").value

        self.latest_voltages: "list[float] | None" = None
        self.latest_centroid: "tuple[float, float] | None" = None
        self.latest_zone_index: "int | None" = None

        self.create_subscription(TactileStamped, in_topic, self._on_voltages, 10)
        self.create_subscription(TactileProcessed, processed_topic, self._on_processed, 10)

        self.get_logger().info(
            f"tactile_calibration_gui: voltages<-'{in_topic}' processed<-'{processed_topic}'"
        )
        self.get_logger().warn(
            "No reference F/T sensor is wired in yet -- wrench values come from "
            "the manual entry panel. Pose is stored as an identity placeholder. "
            "See this module's docstring (Step 9 scope)."
        )

    def _on_voltages(self, msg: TactileStamped) -> None:
        self.latest_voltages = list(msg.tactile.data)

    def _on_processed(self, msg: TactileProcessed) -> None:
        self.latest_centroid = (msg.centroid.x, msg.centroid.y)
        self.latest_zone_index = msg.zone_index


class CalibrationWindow(QMainWindow):
    def __init__(self, node: CalibrationSubscriberNode) -> None:
        super().__init__()
        self._node = node
        self.setWindowTitle("tactile_ws -- calibration acquisition GUI (Step 9)")

        self.project_data = ProjectData(
            finger_info=FingerInfo(finger_id=node.finger_id, taxel_pitch=node.pitch),
            calib_config=CalibConfig(),
        )

        central = QWidget()
        root = QHBoxLayout(central)

        # --- left: live heatmap (reused directly from Step 7) ---
        self.heatmap = HeatmapWidget(node.pitch, node.voltage_max)
        root.addWidget(self.heatmap)

        # --- right: manual wrench entry + controls ---
        right = QVBoxLayout()

        warn = QLabel(
            "MANUAL WRENCH ENTRY\n"
            "(no reference F/T sensor wired in yet -- Step 9 scope,\n"
            "see this module's docstring)"
        )
        warn.setStyleSheet("color: darkorange; font-weight: bold;")
        right.addWidget(warn)

        form = QFormLayout()
        self.spin_boxes: "dict[str, QDoubleSpinBox]" = {}
        for label in WRENCH_FIELDS:
            box = QDoubleSpinBox()
            box.setRange(-100.0, 100.0)
            box.setDecimals(4)
            box.setSingleStep(0.01)
            form.addRow(label, box)
            self.spin_boxes[label] = box
        right.addLayout(form)

        self.status_label = QLabel("Waiting for data...")
        right.addWidget(self.status_label)

        self.fn_preview_label = QLabel("fn bin: n/a")
        right.addWidget(self.fn_preview_label)

        self.counts_label = QLabel("Total samples: 0")
        right.addWidget(self.counts_label)

        self.accept_button = QPushButton("Accept Sample")
        self.accept_button.setEnabled(False)
        self.accept_button.clicked.connect(self._on_accept)
        right.addWidget(self.accept_button)

        self.save_button = QPushButton("Save Project...")
        self.save_button.clicked.connect(self._on_save)
        right.addWidget(self.save_button)

        right.addStretch()
        root.addLayout(right)

        self.setCentralWidget(central)
        self.resize(700, 450)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(33)  # ~30 Hz, same polling pattern as monitor_gui (Step 7)

    def _current_wrench(self) -> "list[float]":
        return [self.spin_boxes[k].value() for k in WRENCH_FIELDS]

    def _on_timer(self) -> None:
        rclpy.spin_once(self._node, timeout_sec=0.0)
        self.heatmap.set_data(self._node.latest_voltages, self._node.latest_centroid)

        fz = self.spin_boxes["fz"].value()
        fn_index = compute_fn_index(fz, self.project_data.calib_config.fn_intervals)
        self.fn_preview_label.setText(
            f"fn bin: {fn_index if fn_index != -1 else 'OUT OF RANGE'}"
        )

        zone = self._node.latest_zone_index
        if self._node.latest_voltages is None:
            self.status_label.setText("Waiting for data...")
            self.accept_button.setEnabled(False)
        else:
            centroid = self._node.latest_centroid
            zone_text = "n/a" if zone is None else str(zone)
            centroid_text = "n/a" if centroid is None else f"({centroid[0]:.4f}, {centroid[1]:.4f}) m"
            self.status_label.setText(f"centroid: {centroid_text}   zone: {zone_text}")
            self.accept_button.setEnabled(zone is not None and zone != -1 and fn_index != -1)

    def _on_accept(self) -> None:
        if self._node.latest_voltages is None or self._node.latest_zone_index is None:
            return

        zone_index = self._node.latest_zone_index
        fz = self.spin_boxes["fz"].value()
        fn_index = compute_fn_index(fz, self.project_data.calib_config.fn_intervals)

        if zone_index == -1 or fn_index == -1:
            QMessageBox.warning(
                self, "Invalid sample", "zone or fn is out of the configured calibration area."
            )
            return

        self.project_data.add_sample(
            timestamp=time.time(),
            voltages_rect=self._node.latest_voltages,
            wrench=self._current_wrench(),
            pose=IDENTITY_POSE,
            zone_index=zone_index,
            fn_index=fn_index,
        )
        self.counts_label.setText(f"Total samples: {self.project_data.num_samples()}")

    def _on_save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save calibration project", "/workspace/calibration/session"
        )
        if not path:
            return
        self.project_data.save(path)
        QMessageBox.information(
            self,
            "Saved",
            f"Saved {self.project_data.num_samples()} samples to {path}.h5 / {path}.yaml",
        )


def main(args: "list[str] | None" = None) -> None:
    rclpy.init(args=args)
    node = CalibrationSubscriberNode()

    app = QApplication(sys.argv)
    window = CalibrationWindow(node)
    window.show()

    exit_code = app.exec()

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

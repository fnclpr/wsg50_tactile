"""
Python-native calibration dataset structure -- the direct equivalent
of the legacy MATLAB struct_projectData.m / struct_calib_data.m, but
using a FLAT sample table (one row per sample, zone_index/fn_index as
plain columns) instead of MATLAB's pre-binned {zone, fn} cell-array
grid.

ENGINEERING DECISION (deviation from legacy STORAGE layout, not from
legacy USAGE): zone_index and fn_index are DERIVED from each sample's
centroid and normal force (via tactile_core.processing.zoning), so
committing to a pre-binned grid at storage time is unnecessarily
rigid -- it would need reshaping every time zone_radius_intervals or
fn_intervals changes. A flat table lets you re-derive bins on demand
(boolean-mask filtering, see samples_in_bin()) and is actually MORE
faithful to how the legacy pipeline itself operates downstream:
mergeCalibData.m already flattens every {zone,fn} cell into one matrix
before decimation/training ever touches it. So a flat table matches
the real consumption pattern, even though it differs from the
historical storage layout.

Format: one HDF5 file (numeric sample arrays) + one YAML sidecar
(finger_info, calibration config, schema version, provenance) per
calibration session, per Section 11 of the project plan.

Sentinel convention: zone_index == -1 means "outside the calibrated
area" (matches tactile_msgs/TactileProcessed's convention from Step
6); fn_index == -1 means "outside the configured fn_intervals". Both
map from tactile_core.processing's NaN convention (Python NaN has no
clean HDF5/int32 equivalent).
"""
from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Union

import h5py
import numpy as np
import yaml

SCHEMA_VERSION = 1

NUM_TAXELS = 25
WRENCH_DIM = 6  # [fx, fy, fz, taux, tauy, tauz]
POSE_DIM = 7  # [x, y, z, qx, qy, qz, qw]


@dataclass
class FingerInfo:
    """Direct equivalent of struct_finger_info.m's fields.

    silicon_sphere_radius and taxel_pitch are per-FINGER calibration
    values (see PAPER AMBIGUITY 1 in the project analysis doc: two
    different legacy defaults, 0.05m and 0.025m, exist for different
    hardware revisions) -- never treat these as universal constants.
    """

    finger_id: str = "unknown"
    silicon_sphere_radius: float = 0.05  # meters, matches struct_finger_info.m's default
    broken_cells: "list[int]" = field(default_factory=list)  # 1-indexed, matches legacy convention
    taxel_pitch: float = 0.007  # meters, matches struct_finger_info.m's default
    z_coord_sphere_frame_wrt_calib_sensor_frame: float = 0.0316183 - 0.05  # matches legacy default formula


@dataclass
class CalibConfig:
    """Direct equivalent of struct_calib_data.m's non-sample fields."""

    fn_intervals: "list[float]" = field(default_factory=lambda: [0.0, 2.0, 4.0, 6.0, 8.5])
    zone_angle_bound_lines: "list[float]" = field(
        default_factory=lambda: [
            0.7853981633974483,  # pi/4
            2.356194490192345,  # 3*pi/4
            3.9269908169872414,  # 5*pi/4
            5.497787143782138,  # 7*pi/4
        ]
    )  # matches create_empty_project.m
    zone_radius_intervals: "list[float]" = field(default_factory=lambda: [0.0015, 0.0045, 0.01])
    mu: float = 1.0
    alpha: float = 2 * 0.0051 * 0.32 * 1.0  # matches struct_plot_data.m's default (mu=1)
    gamma: float = 0.2569


@dataclass
class ProjectData:
    """The Python-native calibration dataset: metadata + a flat sample table."""

    finger_info: FingerInfo = field(default_factory=FingerInfo)
    calib_config: CalibConfig = field(default_factory=CalibConfig)

    timestamps: np.ndarray = field(default_factory=lambda: np.zeros((0,), dtype=np.float64))
    voltages_rect: np.ndarray = field(default_factory=lambda: np.zeros((0, NUM_TAXELS), dtype=np.float32))
    wrench: np.ndarray = field(default_factory=lambda: np.zeros((0, WRENCH_DIM), dtype=np.float64))
    pose: np.ndarray = field(default_factory=lambda: np.zeros((0, POSE_DIM), dtype=np.float64))
    zone_index: np.ndarray = field(default_factory=lambda: np.zeros((0,), dtype=np.int32))
    fn_index: np.ndarray = field(default_factory=lambda: np.zeros((0,), dtype=np.int32))

    def num_samples(self) -> int:
        return int(self.timestamps.shape[0])

    def add_sample(
        self,
        timestamp: float,
        voltages_rect: "np.ndarray | list[float]",
        wrench: "np.ndarray | list[float]",
        pose: "np.ndarray | list[float]",
        zone_index: int,
        fn_index: int,
    ) -> None:
        """Append one sample.

        Uses simple array concatenation -- fine for calibration-session
        data sizes (thousands to tens of thousands of samples; this is
        NOT a hot real-time path, it's called once per accepted
        calibration sample during an operator-driven acquisition
        session in Step 9).
        """
        voltages_rect = np.asarray(voltages_rect, dtype=np.float32).reshape(1, NUM_TAXELS)
        wrench = np.asarray(wrench, dtype=np.float64).reshape(1, WRENCH_DIM)
        pose = np.asarray(pose, dtype=np.float64).reshape(1, POSE_DIM)

        self.timestamps = np.append(self.timestamps, [float(timestamp)])
        self.voltages_rect = np.vstack([self.voltages_rect, voltages_rect])
        self.wrench = np.vstack([self.wrench, wrench])
        self.pose = np.vstack([self.pose, pose])
        self.zone_index = np.append(self.zone_index, [int(zone_index)]).astype(np.int32)
        self.fn_index = np.append(self.fn_index, [int(fn_index)]).astype(np.int32)

    def samples_in_bin(self, zone_index: int, fn_index: int) -> "ProjectData":
        """Return a NEW ProjectData containing only samples in the
        given (zone, fn) bin -- the on-demand equivalent of indexing
        into MATLAB's calib_data.voltage_rect_cell{zone,fn}."""
        mask = (self.zone_index == zone_index) & (self.fn_index == fn_index)
        return ProjectData(
            finger_info=self.finger_info,
            calib_config=self.calib_config,
            timestamps=self.timestamps[mask],
            voltages_rect=self.voltages_rect[mask],
            wrench=self.wrench[mask],
            pose=self.pose[mask],
            zone_index=self.zone_index[mask],
            fn_index=self.fn_index[mask],
        )

    def save(self, path: "Union[str, Path]") -> None:
        """Write <path>.h5 (sample arrays) + <path>.yaml (metadata)."""
        path = Path(path)
        h5_path = path.with_suffix(".h5")
        yaml_path = path.with_suffix(".yaml")

        with h5py.File(h5_path, "w") as f:
            f.attrs["schema_version"] = SCHEMA_VERSION
            f.create_dataset("timestamps", data=self.timestamps)
            f.create_dataset("voltages_rect", data=self.voltages_rect)
            f.create_dataset("wrench", data=self.wrench)
            f.create_dataset("pose", data=self.pose)
            f.create_dataset("zone_index", data=self.zone_index)
            f.create_dataset("fn_index", data=self.fn_index)

        metadata = {
            "schema_version": SCHEMA_VERSION,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "num_samples": self.num_samples(),
            "finger_info": asdict(self.finger_info),
            "calib_config": asdict(self.calib_config),
            "h5_file": h5_path.name,
        }
        with open(yaml_path, "w") as f:
            yaml.safe_dump(metadata, f, sort_keys=False)

    @classmethod
    def load(cls, path: "Union[str, Path]") -> "ProjectData":
        path = Path(path)
        yaml_path = path.with_suffix(".yaml")
        h5_path = path.with_suffix(".h5")

        with open(yaml_path) as f:
            metadata = yaml.safe_load(f)

        if metadata["schema_version"] != SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported schema_version {metadata['schema_version']} "
                f"(this code supports {SCHEMA_VERSION}). Write a migration, "
                "don't silently reinterpret the data."
            )

        finger_info = FingerInfo(**metadata["finger_info"])
        calib_config = CalibConfig(**metadata["calib_config"])

        with h5py.File(h5_path, "r") as f:
            return cls(
                finger_info=finger_info,
                calib_config=calib_config,
                timestamps=f["timestamps"][:],
                voltages_rect=f["voltages_rect"][:],
                wrench=f["wrench"][:],
                pose=f["pose"][:],
                zone_index=f["zone_index"][:],
                fn_index=f["fn_index"][:],
            )

"""
Tests for tactile_core.calibration.dataset.

Split deliberately into two groups:
  - pure-Python/numpy logic (add_sample, samples_in_bin, dataclass
    defaults) -- runnable anywhere numpy is installed.
  - save()/load() round-trip -- requires h5py. If h5py is not
    installed in your environment, these will fail at import/collection
    time; install it (it's already in docker/requirements.txt for the
    dev container) rather than skip them silently.
"""
import math
import os
import tempfile

import numpy as np

from tactile_core.calibration.dataset import (
    NUM_TAXELS,
    POSE_DIM,
    WRENCH_DIM,
    CalibConfig,
    FingerInfo,
    ProjectData,
)


def test_finger_info_defaults_match_legacy_formula():
    fi = FingerInfo()
    # z_coord default in struct_finger_info.m: 0.0316183 - silicon_sphere_radius
    assert math.isclose(fi.z_coord_sphere_frame_wrt_calib_sensor_frame, 0.0316183 - 0.05, rel_tol=1e-12)
    assert fi.silicon_sphere_radius == 0.05
    assert fi.taxel_pitch == 0.007
    assert fi.broken_cells == []


def test_calib_config_alpha_default_matches_legacy_formula():
    cc = CalibConfig()
    # struct_plot_data.m: alpha = 2*0.0051*0.32*mu, with mu=1
    expected_alpha = 2 * 0.0051 * 0.32 * 1.0
    assert math.isclose(cc.alpha, expected_alpha, rel_tol=1e-12)
    assert cc.gamma == 0.2569
    assert cc.fn_intervals == [0.0, 2.0, 4.0, 6.0, 8.5]


def test_empty_project_data_has_zero_samples():
    pd = ProjectData()
    assert pd.num_samples() == 0
    assert pd.voltages_rect.shape == (0, NUM_TAXELS)
    assert pd.wrench.shape == (0, WRENCH_DIM)
    assert pd.pose.shape == (0, POSE_DIM)


def test_add_sample_appends_correctly():
    pd = ProjectData()
    pd.add_sample(
        timestamp=1.0,
        voltages_rect=np.arange(25, dtype=float) * 0.1,
        wrench=[0.0, 0.0, -2.5, 0.0, 0.0, 0.01],
        pose=[0.001, 0.002, 0.0, 0.0, 0.0, 0.0, 1.0],
        zone_index=3,
        fn_index=2,
    )
    pd.add_sample(
        timestamp=2.0,
        voltages_rect=np.arange(25, dtype=float) * 0.2,
        wrench=[0.1, 0.0, -3.0, 0.0, 0.0, 0.02],
        pose=[0.002, 0.003, 0.0, 0.0, 0.0, 0.0, 1.0],
        zone_index=3,
        fn_index=3,
    )
    assert pd.num_samples() == 2
    np.testing.assert_allclose(pd.timestamps, [1.0, 2.0])
    np.testing.assert_allclose(pd.voltages_rect[0], np.arange(25) * 0.1, atol=1e-6)
    np.testing.assert_allclose(pd.wrench[1], [0.1, 0.0, -3.0, 0.0, 0.0, 0.02])
    assert pd.zone_index.tolist() == [3, 3]
    assert pd.fn_index.tolist() == [2, 3]


def test_samples_in_bin_filters_correctly():
    pd = ProjectData()
    # zone 1: 2 samples in fn bin 1, 1 sample in fn bin 2
    # zone 2: 1 sample in fn bin 1
    pd.add_sample(1.0, np.zeros(25), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=1)
    pd.add_sample(2.0, np.ones(25), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=1)
    pd.add_sample(3.0, np.full(25, 2.0), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=2)
    pd.add_sample(4.0, np.full(25, 3.0), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=2, fn_index=1)

    bin_1_1 = pd.samples_in_bin(zone_index=1, fn_index=1)
    assert bin_1_1.num_samples() == 2
    np.testing.assert_allclose(bin_1_1.timestamps, [1.0, 2.0])

    bin_1_2 = pd.samples_in_bin(zone_index=1, fn_index=2)
    assert bin_1_2.num_samples() == 1
    np.testing.assert_allclose(bin_1_2.timestamps, [3.0])

    bin_2_1 = pd.samples_in_bin(zone_index=2, fn_index=1)
    assert bin_2_1.num_samples() == 1
    np.testing.assert_allclose(bin_2_1.timestamps, [4.0])

    bin_9_9 = pd.samples_in_bin(zone_index=9, fn_index=9)
    assert bin_9_9.num_samples() == 0

    # samples_in_bin must carry the SAME metadata (not reset to defaults)
    assert bin_1_1.finger_info is pd.finger_info
    assert bin_1_1.calib_config is pd.calib_config


def test_save_load_roundtrip():
    """Requires h5py. If this fails with ModuleNotFoundError, install
    h5py (it's in docker/requirements.txt) -- do not interpret that as
    a real test failure."""
    pd = ProjectData(
        finger_info=FingerInfo(finger_id="F999_test", silicon_sphere_radius=0.04, broken_cells=[3, 17]),
        calib_config=CalibConfig(mu=0.65),
    )
    pd.add_sample(
        timestamp=123.456,
        voltages_rect=np.linspace(0, 1.9, 25),
        wrench=[0.1, -0.2, -3.5, 0.001, -0.002, 0.03],
        pose=[0.001, -0.002, 0.0, 0.0, 0.0, 0.707, 0.707],
        zone_index=5,
        fn_index=2,
    )
    pd.add_sample(
        timestamp=124.0,
        voltages_rect=np.linspace(0.1, 2.0, 25),
        wrench=[0.15, -0.25, -3.6, 0.002, -0.003, 0.035],
        pose=[0.0011, -0.0021, 0.0, 0.0, 0.0, 0.707, 0.707],
        zone_index=5,
        fn_index=2,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test_session")
        pd.save(path)

        assert os.path.exists(path + ".h5")
        assert os.path.exists(path + ".yaml")

        loaded = ProjectData.load(path)

    assert loaded.num_samples() == pd.num_samples()
    assert loaded.finger_info == pd.finger_info
    assert loaded.calib_config == pd.calib_config
    np.testing.assert_allclose(loaded.timestamps, pd.timestamps)
    np.testing.assert_allclose(loaded.voltages_rect, pd.voltages_rect, atol=1e-6)
    np.testing.assert_allclose(loaded.wrench, pd.wrench)
    np.testing.assert_allclose(loaded.pose, pd.pose)
    assert loaded.zone_index.tolist() == pd.zone_index.tolist()
    assert loaded.fn_index.tolist() == pd.fn_index.tolist()


def test_load_rejects_wrong_schema_version():
    """Requires h5py -- see note on test_save_load_roundtrip."""
    pd = ProjectData()
    pd.add_sample(1.0, np.zeros(25), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=1)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "bad_version")
        pd.save(path)

        # Corrupt the schema_version in the saved YAML sidecar.
        import yaml as _yaml

        with open(path + ".yaml") as f:
            metadata = _yaml.safe_load(f)
        metadata["schema_version"] = 999
        with open(path + ".yaml", "w") as f:
            _yaml.safe_dump(metadata, f)

        try:
            ProjectData.load(path)
            raise AssertionError("expected ValueError for mismatched schema_version")
        except ValueError:
            pass

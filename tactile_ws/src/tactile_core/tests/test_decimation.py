"""
test_1d_two_clusters_hand_derived is fully hand-derived by tracing the
paper's literal MATLAB algorithm step by step (see comments) -- this
is the primary correctness check. The other tests check the general
mathematical PROPERTY the algorithm must satisfy (Eq. 13: every pair
of kept points is farther apart than radius) on a larger synthetic
dataset, plus edge cases (identical points, already-separated points,
radius=0).
"""
import numpy as np

from tactile_core.calibration.decimation import bubble_decimation, decimate_project_data
from tactile_core.calibration.dataset import ProjectData


def test_1d_two_clusters_hand_derived():
    # inputs = [0, 0.5, 1.0, 10.0], radius = 1.0 (radius_square = 1.0)
    #
    # Trace:
    #   actual_index = 0 (value 0.0). Keep it.
    #   remaining = [1, 2, 3] (values 0.5, 1.0, 10.0)
    #   dist_sq to 0.0:        [0.25,  1.0,  100.0]
    #   > radius_square(1.0):  [False, False, True]
    #   -> index 1 (0.5) eliminated (0.25 not > 1.0)
    #   -> index 2 (1.0) eliminated (1.0 is NOT > 1.0 -- strict inequality!)
    #   -> index 3 (10.0) survives (100.0 > 1.0)
    #
    #   actual_index = 3 (only remaining). Keep it. No remaining left. Done.
    #
    # Expected mask_keep: [True, False, False, True]
    inputs = np.array([[0.0], [0.5], [1.0], [10.0]])
    mask = bubble_decimation(inputs, radius=1.0)
    assert mask.tolist() == [True, False, False, True]


def test_exactly_at_radius_is_eliminated_not_kept():
    # Distance exactly equal to radius must be eliminated (paper uses
    # strict `>`, not `>=`) -- this is the same fact exercised inside
    # the hand-derived test above, isolated here for clarity.
    inputs = np.array([[0.0], [2.0]])
    mask = bubble_decimation(inputs, radius=2.0)
    assert mask.tolist() == [True, False]


def test_radius_zero_removes_only_exact_duplicates():
    inputs = np.array([[1.0, 1.0], [1.0, 1.0], [5.0, 5.0]])
    mask = bubble_decimation(inputs, radius=0.0)
    # first duplicate kept, second eliminated (dist_sq=0, not > 0), distinct point kept
    assert mask.tolist() == [True, False, True]


def test_all_identical_points_keep_exactly_one():
    inputs = np.tile([1.0, 2.0, 3.0], (10, 1))
    mask = bubble_decimation(inputs, radius=0.5)
    assert mask.sum() == 1


def test_already_separated_points_all_survive():
    # Points 100 apart, radius 1 -- decimation should be a no-op.
    inputs = np.array([[0.0], [100.0], [200.0], [300.0]])
    mask = bubble_decimation(inputs, radius=1.0)
    assert mask.tolist() == [True, True, True, True]


def test_kept_points_satisfy_pairwise_separation_property():
    # Eq. 13's actual guarantee, checked on a larger synthetic dataset:
    # every pair of KEPT points must be strictly farther than radius apart.
    rng = np.random.default_rng(42)
    inputs = rng.uniform(-5.0, 5.0, size=(200, 3))
    radius = 0.8

    mask = bubble_decimation(inputs, radius)
    kept = inputs[mask]

    assert kept.shape[0] >= 1
    # pairwise distances among kept points only
    diffs = kept[:, None, :] - kept[None, :, :]
    dist = np.sqrt(np.sum(diffs**2, axis=-1))
    np.fill_diagonal(dist, np.inf)  # ignore self-distance
    assert np.all(dist > radius), f"minimum pairwise distance {dist.min()} <= radius {radius}"

    # sanity: decimation should have actually reduced a dense random set
    assert kept.shape[0] < inputs.shape[0]


def test_decimate_project_data_applies_per_bin_independently():
    pd = ProjectData()

    # bin (zone=1, fn=1): two near-duplicate voltage vectors + one far one
    pd.add_sample(1.0, np.zeros(25), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=1)
    pd.add_sample(2.0, np.full(25, 0.01), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=1)
    pd.add_sample(3.0, np.full(25, 5.0), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=1, fn_index=1)

    # bin (zone=2, fn=1): two points identical to bin (1,1)'s near-duplicates,
    # but in a DIFFERENT bin -- must be decimated independently, not against bin (1,1)
    pd.add_sample(4.0, np.zeros(25), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=2, fn_index=1)
    pd.add_sample(5.0, np.full(25, 0.01), np.zeros(6), [0, 0, 0, 0, 0, 0, 1], zone_index=2, fn_index=1)

    # radius chosen so sqrt(25*0.01^2)=0.05 < radius < sqrt(25*5.0^2)=25.0
    reduced = decimate_project_data(pd, radius=0.1)

    # bin (1,1): 3 samples -> the two near-duplicates collapse to 1, the far one survives -> 2 kept
    # bin (2,1): 2 samples -> the near-duplicates collapse to 1 kept
    assert reduced.num_samples() == 3

    bin_1_1 = reduced.samples_in_bin(1, 1)
    bin_2_1 = reduced.samples_in_bin(2, 1)
    assert bin_1_1.num_samples() == 2
    assert bin_2_1.num_samples() == 1

    # the "far" sample (timestamp 3.0) must have survived bin (1,1)'s decimation
    assert 3.0 in bin_1_1.timestamps.tolist()

    # metadata must be preserved on the returned object
    assert reduced.finger_info is pd.finger_info
    assert reduced.calib_config is pd.calib_config

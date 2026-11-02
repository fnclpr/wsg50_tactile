"""
Direct port of the bubble-based decimation algorithm from Costanzo et
al., Sensors 2019, 19, 966, Section 3.2, Eq. (10)-(13), including its
literal published MATLAB listing (paper page 13-14):

    function [inputs, targets, mask_keep] = decimation(inputs, targets, radius)
    % Bubble-based decimation function, Ts = {(inputs_i, targets_i)}
    %Initialization
    radius_square = radius^2;
    mask_keep = false(1, size(inputs,2));
    mask_not_computed = ~mask_keep;
    %Repeat until process all samples
    while any(mask_not_computed)
        actual_index = find(mask_not_computed, 1);
        mask_keep(actual_index) = true;
        mask_not_computed(actual_index) = false;
        mask_not_computed(mask_not_computed) = ...
            sum((inputs(:,mask_not_computed) - inputs(:,actual_index)).^2) > radius_square;
    end
    %select only good samples
    inputs = inputs(:, mask_keep);
    targets = targets(:, mask_keep);
    end

Equation form (Eq. 10-13): given a training set Ts = {(v_i, w_i)},
i in I_Ts = {1..N}, find the maximal subset T*s such that every pair of
kept inputs is farther apart than radius r:

    I_T*s = {j in I_Ts : ||v_j - v_k|| > r  for all k in I_Ts, k != j}

GENUINE GAP, not guessed at: the legacy repo's sun_finger_decim.m calls
sun_train_decim(inputs, targets, radius, input_scale, target_scale) --
a function with input/target NORMALIZATION options that is referenced
but was never provided to me (only the outer per-zone/per-fn loop in
sun_finger_decim.m exists in the material I have). The paper itself
notes normalization matters "for a heterogeneous input space" (Section
3.2, one paragraph after the listing above). This module implements
ONLY the paper's published, unnormalized algorithm exactly as listed.
If/when sun_train_decim.m's actual normalization scheme is available,
it should be added as an explicit pre-processing step BEFORE calling
bubble_decimation, not silently folded in here.

ARRAY LAYOUT NOTE (ENGINEERING DECISION, not an algorithm change):
the MATLAB code above stores samples as columns (inputs(:,i) is the
ith sample). This module uses NumPy's more idiomatic row-per-sample
layout (inputs[i] is the ith sample) throughout -- purely a transpose
of storage convention, verified not to change the algorithm's
behavior (see test_decimation.py's hand-derived cases).
"""
from __future__ import annotations

import numpy as np

from .dataset import ProjectData


def bubble_decimation(inputs: np.ndarray, radius: float) -> np.ndarray:
    """Greedy bubble decimation, direct port of the paper's `decimation()`.

    Parameters
    ----------
    inputs: (N, D) array, one row per sample (see module docstring's
        array-layout note).
    radius: bubble radius r. Two kept samples are guaranteed to satisfy
        ||v_j - v_k|| > radius (strict), matching the paper's `>` (not
        `>=`) comparison exactly -- points at EXACTLY `radius` apart
        are eliminated, not kept.

    Returns
    -------
    np.ndarray, shape (N,), dtype bool: True for samples to KEEP.
    """
    inputs = np.asarray(inputs, dtype=float)
    n = inputs.shape[0]
    radius_square = radius**2

    mask_keep = np.zeros(n, dtype=bool)
    mask_not_computed = np.ones(n, dtype=bool)

    while np.any(mask_not_computed):
        actual_index = int(np.argmax(mask_not_computed))  # first True index
        mask_keep[actual_index] = True
        mask_not_computed[actual_index] = False

        remaining_idx = np.flatnonzero(mask_not_computed)
        if remaining_idx.size == 0:
            break

        dist_sq = np.sum((inputs[remaining_idx] - inputs[actual_index]) ** 2, axis=1)
        # Direct translation of:
        #   mask_not_computed(mask_not_computed) = sum(...) > radius_square
        # i.e. replace (not just AND-eliminate) the not_computed flags for
        # exactly the currently-remaining indices with "is far enough".
        mask_not_computed[remaining_idx] = dist_sq > radius_square

    return mask_keep


def decimate_project_data(project_data: ProjectData, radius: float) -> ProjectData:
    """Apply bubble_decimation independently within each (zone_index,
    fn_index) bin present in project_data, per the paper's guidance
    (Section 3.2, paragraph after the listing): "this algorithm can be
    applied separately on the data of each 3D space defined in Section
    3.1. In this way the computational load of the decimation is
    reduced."

    Distance is computed in the 25-dim voltages_rect INPUT space
    (matches the paper's "inputs" -- NOT the wrench/target space).

    Returns a NEW ProjectData containing only the kept samples (bins
    concatenated in sorted (zone, fn) order; original relative order
    is preserved within each bin).
    """
    unique_bins = sorted(
        {(int(z), int(f)) for z, f in zip(project_data.zone_index, project_data.fn_index)}
    )

    kept = ProjectData(finger_info=project_data.finger_info, calib_config=project_data.calib_config)

    for zone, fn in unique_bins:
        bin_data = project_data.samples_in_bin(zone, fn)
        if bin_data.num_samples() == 0:
            continue

        mask = bubble_decimation(bin_data.voltages_rect, radius)

        for i in np.flatnonzero(mask):
            kept.add_sample(
                timestamp=bin_data.timestamps[i],
                voltages_rect=bin_data.voltages_rect[i],
                wrench=bin_data.wrench[i],
                pose=bin_data.pose[i],
                zone_index=int(bin_data.zone_index[i]),
                fn_index=int(bin_data.fn_index[i]),
            )

    return kept

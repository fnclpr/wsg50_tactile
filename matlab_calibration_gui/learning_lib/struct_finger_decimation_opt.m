function [finger_decimation_opt] = struct_finger_decimation_opt(finger_decimation_opt)
%GET_FINGER_DECIMATION_OPT Summary of this function goes here
%   Detailed explanation goes here

%% Input
if nargin < 1
    finger_decimation_opt = struct;
end

if ~isstruct(finger_decimation_opt)
    error('finger_decimation_opt is not struct')
end

%% build struct

% use raw voltages for decimation
if ~isfield(finger_decimation_opt, 'b_raw_voltage')
    finger_decimation_opt.b_raw_voltage = false;
end

% min_targets
if ~isfield(finger_decimation_opt, 'min_wrench')
    finger_decimation_opt.min_wrench = -inf*ones(1,4);
end

% max_targets
if ~isfield(finger_decimation_opt, 'max_wrench')
    finger_decimation_opt.max_wrench = +inf*ones(1,4);
end

% max_targets
if ~isfield(finger_decimation_opt, 'decimation_radius')
    finger_decimation_opt.decimation_radius = 0.02;
end

% input_scale
if ~isfield(finger_decimation_opt, 'input_scale')
    finger_decimation_opt.input_scale = 'minmax';
end

% target_scale
if ~isfield(finger_decimation_opt, 'target_scale')
    finger_decimation_opt.target_scale = 'minmax';
end

end


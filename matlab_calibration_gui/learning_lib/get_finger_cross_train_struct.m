function finger_cross_train = get_finger_cross_train_struct(finger_cross_train)
%GET_FINGER_TRAIN_STRUCT Summary of this function goes here
%   Detailed explanation goes here

%% Input
if nargin < 1
    finger_cross_train = struct;
end

if ~isstruct(finger_cross_train)
    error('finger_cross_train is not struct')
end

%% build struct

% Input file from the GUI
if ~isfield(finger_cross_train, 'input_file')
    finger_cross_train.input_file = 'INSERT INPUT FILE HERE';
end

% percentage of cross validation data
if ~isfield(finger_cross_train, 'cross_valid_perc')
    finger_cross_train.cross_valid_perc = 30/100;
end

% train_file
if ~isfield(finger_cross_train, 'train_file')
    finger_cross_train.train_file = [];
end

% cross_valid_file
if ~isfield(finger_cross_train, 'cross_valid_file')
    finger_cross_train.cross_valid_file = [];
end

% decimated_cross_valid_file
if ~isfield(finger_cross_train, 'decimated_cross_valid_file')
    finger_cross_train.decimated_cross_valid_file = [];
end

% decimation opt for the cross valid set
if ~isfield(finger_cross_train, 'cross_valid_decimation_opt')
    finger_cross_train.cross_valid_decimation_opt = get_finger_decimation_opt();
else
    finger_cross_train.cross_valid_decimation_opt = get_finger_decimation_opt(finger_cross_train.cross_valid_decimation_opt);
end

% percentage of zeros for the cross valid set
if ~isfield(finger_cross_train, 'cross_valid_perc_zeros')
    finger_cross_train.cross_valid_perc_zeros = 0.6/100;
end

%% Update the finger trains cell

if ~isfield(finger_cross_train, 'finger_trains')
    finger_cross_train.finger_trains = cell(0);
end

if ~iscell(finger_cross_train.finger_trains)
    error('finger_trains is not a cell')
end

for i=1:numel(finger_cross_train.finger_trains)
    finger_cross_train.finger_trains = get_finger_train_struct(finger_cross_train.finger_trains);
end

end


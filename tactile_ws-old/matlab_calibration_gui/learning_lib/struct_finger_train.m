function finger_train = struct_finger_train(finger_train)
%GET_FINGER_TRAIN_STRUCT Summary of this function goes here
%   Detailed explanation goes here

%% Input
if nargin < 1
    finger_train = struct;
end

if ~isstruct(finger_train)
    error('finger_train is not struct')
end

%% build struct

% Input file from the GUI
if ~isfield(finger_train, 'project_data_file')
    finger_train.project_data_file = 'INSERT DATA FILE HERE';
end

% decimated version of the data_file
if ~isfield(finger_train, 'project_data_decimated_file')
    finger_train.project_data_decimated_file = [];
end

% decimation opt for the data_file
if ~isfield(finger_train, 'finger_decimation_opt')
    finger_train.finger_decimation_opt = struct_finger_decimation_opt();
else
    finger_train.finger_decimation_opt = struct_finger_decimation_opt(finger_train.finger_decimation_opt);
end

% perc zero to add to the train data
if ~isfield(finger_train, 'perc_zeros')
    finger_train.perc_zeros = 0.6/100;
end

% use raw voltages in train?
if ~isfield(finger_train, 'b_raw_voltage')
    finger_train.b_raw_voltage = false;
end

% use raw voltages in train?
if ~isfield(finger_train, 'raw_zero_file')
    if finger_train.b_raw_voltage
        finger_train.raw_zero_file = 'INSERT RAW ZERO FILE HERE';
    end
end

% train_opt
if ~isfield(finger_train, 'pca_train_opt')
    finger_train.pca_train_opt = struct_pca_train_opt();
else
    finger_train.pca_train_opt = struct_pca_train_opt(finger_train.pca_train_opt);
end

%% ADD STUFF FROM userData

b_need_to_load = ~isfield(finger_train, 'finger_id') || ~isfield(finger_train, 'broken_cells');

if b_need_to_load && ~isequal(finger_train.project_data_file, 'INSERT DATA FILE HERE')
    loaded_file = load(finger_train.project_data_file);
    finger_train.finger_id = loaded_file.projectData.finger_info.finger_id;
    finger_train.broken_cells = loaded_file.projectData.finger_info.broken_cells;
end

%% FIX RAW_VOLTAGE
finger_train.decimation_opt.b_raw_voltage = finger_train.b_raw_voltage;

end


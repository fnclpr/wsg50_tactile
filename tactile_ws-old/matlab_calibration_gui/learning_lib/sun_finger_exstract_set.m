function [ inputs, targets, time_inputs, time_targets ] = sun_finger_exstract_set( data_file, perc_zero, b_raw_voltage, raw_zero_file)
%BUILD_TRAIN_SET build the train set from the struct
%   extract inputs and targets.
%   if raw_voltage = true then inputs will be the raw voltages
%   add zeros to the train set using the option perc_zero.
%   NB. if raw_voltage=true you have to provide a raw_zero_file containing
%   the raw voltages corresponding to no wrench
%   Moreover, this function removes bad voltages using
%   finger_info.broken_cells

%% Input
if nargin < 2
    perc_zero = 0;
end

if nargin < 3
    b_raw_voltage = false;
end

%% LOAD DATA
loaded_file = load(data_file);

[  voltages_rect, time_voltages_rect, ...
   voltages_raw, time_voltages_raw, ...
   wrenches, time_wrenches, ...
   poses, time_poses ...
] = mergeCalibData( loaded_file.projectData.calib_data , false);

%% ADD ZEROS
if perc_zero ~=0
Nz = ceil(perc_zero*size(wrenches,2));
if ~b_raw_voltage

    inputs = [voltages_rect , zeros(size(voltages_rect,1),Nz)];
    targets = [wrenches , zeros(size(wrenches,1),Nz)];
    time_inputs = [time_voltages_rect, linspace(time_voltages_rect(end)+1, time_voltages_rect(end)+1+Nz, Nz)];
    time_targets = [time_wrenches, linspace(time_wrenches(end)+1, time_wrenches(end)+1+Nz, Nz)];
    
else
    
    % load zero voltages
    loaded_file_zero = load(raw_zero_file);
    voltages_raw_zero = zeros(size(voltages_raw,1),Nz);
    num_to_add = Nz;
    start_add_index = 1;
    while num_to_add > 0
        num_local_add = min(num_to_add, size(loaded_file_zero.voltages_raw,2));
        voltages_raw_zero(:,start_add_index:(start_add_index+num_local_add-1)) = ...
                    loaded_file_zero.voltages_raw(:,1:num_local_add);
        num_to_add = num_to_add - num_local_add;
        start_add_index = start_add_index + num_local_add;
    end
    % just to check
    if size(voltages_raw_zero,2) ~= Nz; error('load zero raw ERROR!'); end
    %end
    
    inputs = [voltages_raw , voltages_raw_zero];
    targets = [wrenches , zeros(size(wrenches,1),Nz)];
    time_inputs = [time_voltages_raw, linspace(time_voltages_raw(end)+1, time_voltages_raw(end)+1+Nz, Nz)];
    time_targets = [time_wrenches, linspace(time_wrenches(end)+1, time_wrenches(end)+1+Nz, Nz)];
    
end
else % if perc_zero ==0
    if ~b_raw_voltage
        inputs = voltages_rect;
    else
        inputs = voltages_raw;
    end
    targets = wrenches;
    time_inputs = time_voltages_rect;
    time_targets = time_wrenches;
end 

%% Remove bad voltages

inputs(loaded_file.projectData.finger_info.broken_cells,:) = [];


end


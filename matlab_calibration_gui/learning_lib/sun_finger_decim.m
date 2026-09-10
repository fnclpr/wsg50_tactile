function [projectData] = sun_finger_decim(project_data_file, finger_decimation_opt)
% SUN_TRAIN_DECIM decimation for the sun fingers

%% Extract options
min_wrench = finger_decimation_opt.min_wrench;
max_wrench = finger_decimation_opt.max_wrench;
b_raw_voltage = finger_decimation_opt.b_raw_voltage;
decimation_radius = finger_decimation_opt.decimation_radius;
input_scale = finger_decimation_opt.input_scale;
target_scale = finger_decimation_opt.target_scale;

%% LOAD INPUT FILE
t0 = tic;
disp('sun_finger_decim - LOADING INPUT FILE...');
loaded_file = load(project_data_file);
projectData = loaded_file.projectData;
disp(['sun_finger_decim - file loaded in ' num2str(toc(t0)) ' s'])

%% Dependent data
num_zones = compute_num_zones(projectData.calib_data.zone_angle_bound_lines, projectData.calib_data.zone_radius_intervals);

%% Find good volts
% find num_volts
num_volts = -1;
for i=1:num_zones %all zones
   for j=1:(length(projectData.calib_data.fn_intervals)-1) %all fn
       if ~isempty(projectData.calib_data.voltage_rect_cell{i,j})
           num_volts = size(projectData.calib_data.voltage_rect_cell{i,j},1);
           break;
       end
   end
   if num_volts ~= -1
       break;
   end
end
if num_volts == -1
    error('unable to find num_volts!')
end
% mask of good volts
mask_good_volts = true(num_volts,1);
mask_good_volts(projectData.finger_info.broken_cells) = false;
if ~all(mask_good_volts)
    warning('on')
    warning(['sun_train_decim - found bad voltages ' num2str(projectData.finger_info.broken_cells)])
end

%% Different decimation size
radii = decimation_radius(end)*ones(1,(length(projectData.calib_data.fn_intervals)-1));
radii(1:min( numel(radii), numel(decimation_radius) )) = ...
    decimation_radius(1:min( numel(radii), numel(decimation_radius) ));

%% DECIMATION
use_minmax_wrench = ~(all(isinf(min_wrench)) && all(isinf(max_wrench)));
t0 = tic;
disp('sun_finger_decim - Start decimation...');
for i=1:num_zones %all zones
   for j=1:(length(projectData.calib_data.fn_intervals)-1) %all fn
       
       disp(['sun_finger_decim - START zone = ' num2str(i) '/' num2str(num_zones) ' || ' ...
           'interval = ' num2str(j) '/' num2str((length(projectData.calib_data.fn_intervals)-1))]);
       toc(t0);
       
       % delete out interval min-max
       if use_minmax_wrench && ~isempty(projectData.calib_data.wrench_cell{i,j})
       disp('sun_finger_decim - remving out of intervals...');
       delete_index = logical(...
                       sum(...
                        projectData.calib_data.wrench_cell{i,j}([1:3 6],:) ...
                        < min_wrench(:) ...
                        | ...
                        projectData.calib_data.wrench_cell{i,j}([1:3 6],:) ...
                        > ...
                        max_wrench(:) ...
                        ) ... %sum
                        ); %logical
       projectData.calib_data.voltage_rect_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.time_voltage_rect_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.voltage_raw_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.time_voltage_raw_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.wrench_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.time_wrench_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.pose_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.time_pose_cell{i,j}(:,delete_index) = [];
       projectData.calib_data.plot_data.wrench_plot_cell{i,j}(:,delete_index) = [];
       
       disp('sun_finger_decim - remving out of intervals DONE');
       disp(['num deleted = ' num2str(sum(delete_index))]);
       end
       
       %decim
       if b_raw_voltage
           [~, ~, mask_keep] = ...
                sun_train_decim( ...
                    projectData.calib_data.voltage_raw_cell{i,j}(mask_good_volts,:), ...
                    projectData.calib_data.wrench_cell{i,j}, ...
                    radii(j), ...
                    input_scale, ...
                    target_scale ...
                    );
       else
           [~, ~, mask_keep] = ...
                sun_train_decim( ...
                    projectData.calib_data.voltage_rect_cell{i,j}(mask_good_volts,:), ...
                    projectData.calib_data.wrench_cell{i,j}, ...
                    radii(j), ...
                    input_scale, ...
                    target_scale ...
                    );           
       end
       
       % apply decim
       projectData.calib_data.voltage_rect_cell{i,j} = projectData.calib_data.voltage_rect_cell{i,j}(:,mask_keep);
       projectData.calib_data.time_voltage_rect_cell{i,j} = projectData.calib_data.time_voltage_rect_cell{i,j}(:,mask_keep);
       projectData.calib_data.voltage_raw_cell{i,j} = projectData.calib_data.voltage_raw_cell{i,j}(:,mask_keep);
       projectData.calib_data.time_voltage_raw_cell{i,j} = projectData.calib_data.time_voltage_raw_cell{i,j}(:,mask_keep);
       projectData.calib_data.wrench_cell{i,j} = projectData.calib_data.wrench_cell{i,j}(:,mask_keep);
       projectData.calib_data.time_wrench_cell{i,j} = projectData.calib_data.time_wrench_cell{i,j}(:,mask_keep);
       projectData.calib_data.pose_cell{i,j} = projectData.calib_data.pose_cell{i,j}(:,mask_keep);
       projectData.calib_data.time_pose_cell{i,j} = projectData.calib_data.time_pose_cell{i,j}(:,mask_keep);
       projectData.calib_data.plot_data.wrench_plot_cell{i,j} = projectData.calib_data.plot_data.wrench_plot_cell{i,j}(:,mask_keep);
       
   end
end

disp('sun_train_decim - END');
toc(t0);

end


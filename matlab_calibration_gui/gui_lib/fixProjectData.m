function [ projectData ] = fixProjectData( projectData )
%CLEARDATA Summary of this function goes here
%   Detailed explanation goes here

disp('Starting clear data...')
time_start = tic;

[projectData, dependent_data ]  = struct_projectData( projectData );

[  voltages_rect, time_voltages_rect, ...
   voltages_raw, time_voltages_raw, ...
   wrenches, time_wrenches, ...
   poses, time_poses ...
] = mergeCalibData(projectData.calib_data);

wrenches_plot = zeros(3,size(wrenches,2));

mask = zeros(2,length(time_wrenches)); % [zone;interval]
%del_mask = [];
%search bad data and fill mask
disp('Start search...')

%prepare parfor vars
projectData_calib_data_fn_intervals_end = projectData.calib_data.fn_intervals(end);
projectData_gui_data_calib_mode = projectData.gui_data.calib_mode;
projectData_finger_info_taxels_x_coords = projectData.finger_info.taxels_x_coords;
projectData_finger_info_taxels_y_coords = projectData.finger_info.taxels_y_coords;
projectData_finger_info_broken_cells = projectData.finger_info.broken_cells;
projectData_calib_data_zone_angle_bound_lines = projectData.calib_data.zone_angle_bound_lines;
projectData_calib_data_zone_radius_intervals = projectData.calib_data.zone_radius_intervals;
projectData_calib_data_fn_intervals = projectData.calib_data.fn_intervals;
projectData_calib_data_plot_data_mu = projectData.calib_data.plot_data.mu;
projectData_calib_data_plot_data_alpha = projectData.calib_data.plot_data.alpha;
projectData_calib_data_plot_data_gamma = projectData.calib_data.plot_data.gamma;

parfor i = 1:length(time_wrenches)
    
    pose_i = poses(:,i);
    wrench_i = wrenches(:,i);
    
    % if fn too high discard sample
    if abs(wrench_i(3)) >  projectData_calib_data_fn_intervals_end
        mask(:,i) = [nan; nan];
        continue; %fn too high
    end
    
    %compute centroid
    if projectData_gui_data_calib_mode == 1 %MODE_HAND
        centroid = compute_centroid( ...
                    voltages_rect(:,i),...
                    projectData_finger_info_taxels_x_coords,...
                    projectData_finger_info_taxels_y_coords,...
                    projectData_finger_info_broken_cells);
    else
        centroid = pose_i(1:2);
    end
   
    %find zone index
    zone_index = find_geometric_zone(...
                    centroid,...
                    projectData_calib_data_zone_angle_bound_lines, ...
                    projectData_calib_data_zone_radius_intervals);
            
    %if invlaid zone discard sample
    if isnan(zone_index)
        mask(:,i) = [nan; nan];
        continue; %bad zone
    end
            
    %if here I have to save the point
    
    %find fn index
    fn_index = find_interval(projectData_calib_data_fn_intervals,abs(wrench_i(3)));
            
    %compute the plot point
    wrench_plot_point = compute_wrench_plot_point(...
                    wrench_i,...
                    dependent_data.fn_intervals_centers(fn_index),...
                    dependent_data.zone_central_transforms{zone_index},...
                    projectData_calib_data_plot_data_mu,...
                    projectData_calib_data_plot_data_alpha,...
                    projectData_calib_data_plot_data_gamma...
                ); %#ok<PFBNS>
            
    mask(:,i) = [zone_index;fn_index];
    wrenches_plot(:,i) = wrench_plot_point; %#ok<PFOUS>
      
end
disp('End Search')
toc(time_start)

%delete bad data
bad_index = isnan(mask(1,:));
mask(:,bad_index) = [];
voltages_rect(:,bad_index) = [];
time_voltages_rect(:,bad_index) = [];
voltages_raw(:,bad_index) = [];
time_voltages_raw(:,bad_index) = [];
wrenches(:,bad_index) = [];
time_wrenches(:,bad_index) = [];
wrenches_plot(:,bad_index) = [];
poses(:,bad_index) = [];
time_poses(:,bad_index) = [];
disp(['Total bad data = ' num2str(sum(bad_index))]);

%recostruct cell
voltage_rect_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
time_voltage_rect_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
voltage_raw_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
time_voltage_raw_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
wrench_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
time_wrench_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
wrench_plot_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
pose_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));
time_pose_cell = cell(dependent_data.num_zones,length(dependent_data.fn_intervals_centers));

disp('start build cell...')

for i=1:dependent_data.num_zones
   disp([num2str(i) '/' num2str(dependent_data.num_zones)]) 
   this_zone_index = (mask(1,:) == i);
   
   for j=1:length(dependent_data.fn_intervals_centers)
       this_interval_index = (mask(2,:) == j);
       this_index = this_zone_index & this_interval_index;
       
       voltage_rect_cell{i,j} =  voltages_rect(:,this_index);
       time_voltage_rect_cell{i,j} =  time_voltages_rect(:,this_index);
       voltage_raw_cell{i,j} =  voltages_raw(:,this_index);
       time_voltage_raw_cell{i,j} =  time_voltages_raw(:,this_index);
       wrench_cell{i,j} = wrenches(:,this_index);
       time_wrench_cell{i,j} =  time_wrenches(:,this_index);
       pose_cell{i,j} = poses(:,this_index);
       time_pose_cell{i,j} =  time_poses(:,this_index);
       
       wrench_plot_cell{i,j} =  wrenches_plot(:,this_index);
       
   end
   
end

projectData.calib_data.voltage_rect_cell = voltage_rect_cell;
projectData.calib_data.time_voltage_rect_cell = time_voltage_rect_cell;
projectData.calib_data.voltage_raw_cell = voltage_raw_cell;
projectData.calib_data.time_voltage_raw_cell = time_voltage_raw_cell;
projectData.calib_data.wrench_cell = wrench_cell;
projectData.calib_data.time_wrench_cell = time_wrench_cell;
projectData.calib_data.pose_cell = pose_cell;
projectData.calib_data.time_pose_cell = time_pose_cell;

projectData.calib_data.plot_data.wrench_plot_cell = wrench_plot_cell;


disp('END')
toc(time_start)


end


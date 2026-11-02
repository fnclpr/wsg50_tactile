function projectData = update_projectDataVersion(projectData)
%UPDATE_PROJECTDATAVERSION Update the project data from previous version to
%newer
%   Detailed explanation goes here

MAX_VERSION = 3;

if ~isfield(projectData,'version')
    projectData.version = 2; %assume version 2
end

if projectData.version == MAX_VERSION
    return
end

if projectData.version == 2
    
    projectData_ = struct_projectData();
    
    projectData_.finger_info.finger_id = projectData.finger_id;
    projectData_.finger_info.broken_cells = projectData.remove_volts;
    projectData_.finger_info.silicon_sphere_radius = projectData.sf_radius;
    projectData_.finger_info.taxels_x_coords = projectData.XX;
    projectData_.finger_info.taxels_y_coords = projectData.YY;
    projectData_.finger_info.z_coord_sphere_frame_wrt_calib_sensor_frame = projectData.sc_z_sf;
    
    projectData_.calib_data.fn_intervals = projectData.Fn_interval;
    projectData_.calib_data.zone_angle_bound_lines = projectData.angle_bound_lines;
    projectData_.calib_data.zone_radius_intervals = projectData.zone_radius_intervals;
    projectData_.calib_data.voltage_rect_cell = projectData.input_cell;
    projectData_.calib_data.time_voltage_rect_cell = projectData.time_input_cell;
    projectData_.calib_data.voltage_raw_cell = projectData.input_raw_cell;
    projectData_.calib_data.time_voltage_raw_cell = projectData.time_input_cell;
    projectData_.calib_data.wrench_cell = projectData.target_cell;
    projectData_.calib_data.time_wrench_cell = projectData.time_target_cell;
    
    %pose is all nan
    projectData_.calib_data.pose_cell = cellfun(@(c)nan(3+4,size(c,2)) ,projectData.target_cell ,'UniformOutput' ,false);
    projectData_.calib_data.time_pose_cell = projectData.time_target_cell;
    
    projectData_.calib_data.plot_data.mu = projectData.mu_;
    projectData_.calib_data.plot_data.gamma = projectData.gamma_;
    projectData_.calib_data.plot_data.alpha = projectData.alpha_;
    projectData_.calib_data.plot_data.wrench_plot_cell = projectData.target_plot_cell;
    
    projectData_.gui_data.calib_mode = 0; %NONE
    
    projectData = projectData_;
    
    return
end

warning('finger_calib_gui:bad_version', 'Cannot convert project version %d to %d', projectData.version, MAX_VERSION);

end


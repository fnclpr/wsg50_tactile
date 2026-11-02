function [dependent_data] = compute_dependent_data(projectData)
%COMPUTE_DEPENDENT_DATA compute all dependend data from project data
%   Detailed exp

dependent_data = struct;

dependent_data.zone_angle_center_lines = compute_central_angles(projectData.calib_data.zone_angle_bound_lines);

dependent_data.zone_radius_centers = compute_intervals_centers(projectData.calib_data.zone_radius_intervals);

dependent_data.fn_intervals_centers = compute_intervals_centers(projectData.calib_data.fn_intervals);

dependent_data.num_zones = compute_num_zones(projectData.calib_data.zone_angle_bound_lines, projectData.calib_data.zone_radius_intervals);

dependent_data.zone_central_transforms = compute_zone_central_transforms( ...
    dependent_data.zone_radius_centers,...
    projectData.finger_info.silicon_sphere_radius,...
    projectData.finger_info.z_coord_sphere_frame_wrt_calib_sensor_frame,...
    dependent_data.zone_angle_center_lines );

end


function [ trasform_cell ] = compute_zone_central_transforms( zone_radius_centers , silicon_sphere_radius, z_coord_sphere_frame_wrt_calib_sensor_frame,zone_angle_center_lines )
%GENZONETRMATRIX compute calib frame transforms w.r.t. nominal contacts
%frames
%   Detailed explanation goes here

trasform_cell{1} = ([eye(3) , [0;0; -(silicon_sphere_radius+z_coord_sphere_frame_wrt_calib_sensor_frame)] ; [0 0 0 1]]);
for radii = zone_radius_centers
    for alp = zone_angle_center_lines
        [centr_x , centr_y] = pol2cart(alp, radii );
        trasform_cell{end+1} = compute_contact_transform([centr_x; centr_y], silicon_sphere_radius, z_coord_sphere_frame_wrt_calib_sensor_frame); %#ok<*AGROW>
    end
end

end


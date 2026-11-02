function [ finger_info ] = struct_finger_info( finger_info )
%GENUSERDATA Summary of this function goes here
%   Detailed explanation goes here

if nargin < 1 || isempty(finger_info)
   finger_info = struct; 
end

if ~isfield(finger_info,'finger_id')
    finger_info.finger_id = '0';
end

if ~isfield(finger_info,'broken_cells')
    finger_info.broken_cells = [];
end

if ~isfield(finger_info,'silicon_sphere_radius')
    finger_info.silicon_sphere_radius = 0.05; %[m]
end

if ~isfield(finger_info,'taxels_x_coords')
    finger_info.taxels_x_coords = 0.007*repmat([-1 -0.5 0 0.5 1 ] , 5,1); %[m]
end

if ~isfield(finger_info,'taxels_y_coords')
    finger_info.taxels_y_coords = 0.007*repmat([1 0.5 0 -0.5 -1 ]' , 1,5); %[m]
end

if ~isfield(finger_info,'z_coord_sphere_frame_wrt_calib_sensor_frame')
    finger_info.z_coord_sphere_frame_wrt_calib_sensor_frame = 0.0316183 - finger_info.silicon_sphere_radius; %[m]
end

end


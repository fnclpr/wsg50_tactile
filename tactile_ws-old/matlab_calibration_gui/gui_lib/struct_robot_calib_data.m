function [ robot_calib_data ] = struct_robot_calib_data( robot_calib_data )
%GENUSERDATA Summary of this function goes here
%   Detailed explanation goes here

if nargin < 1 || isempty(robot_calib_data)
   robot_calib_data = struct; 
end

if ~isfield(robot_calib_data,'theta_v')
    robot_calib_data.theta_v = [0 deg2rad(10)];
end

if ~isfield(robot_calib_data,'phi_v')
    robot_calib_data.phi_v = [0 pi/2 pi 3*pi/2];
end

if ~isfield(robot_calib_data,'fn_v')
    robot_calib_data.fn_v = -[0.5 2.5];
end

if ~isfield(robot_calib_data,'wrench_v')
    robot_calib_data.wrench_v = cell(1,length(robot_calib_data.fn_v));
    for i=1:length(robot_calib_data.wrench_v)
        robot_calib_data.wrench_v{i} = zeros(3,0);
    end
end
if length(robot_calib_data.wrench_v)~=length(robot_calib_data.fn_v)
    error('finger_calib_gui:bad_data','wrench_v invalid length')
end
for i=1:length(robot_calib_data.wrench_v)
    if size(robot_calib_data.wrench_v{i},1) ~=3
        error('finger_calib_gui:bad_data','wrench_v invalid element size')
    end
end

if ~isfield(robot_calib_data,'i_theta')
    robot_calib_data.i_theta = 1;
end
if ~isfield(robot_calib_data,'i_phi')
    robot_calib_data.i_phi = 1;
end
if ~isfield(robot_calib_data,'i_fn')
    robot_calib_data.i_fn = 1;
end
if ~isfield(robot_calib_data,'i_wrench')
    robot_calib_data.i_wrench = 1;
end

end


function projectData = new_create_empty_project(filename)
%CREATE_EMPTY_PROJECT Summary of this function goes here
%   Detailed explanation goes here

[filepath,name,ext] = fileparts(mfilename('fullpath'));
addpath(filepath);
addpath([filepath '/gui_lib']);


projectData = struct_projectData();

projectData.finger_info.finger_id = 'F401_v2';

projectData.finger_info.silicon_sphere_radius = 0.025;

projectData.calib_data.fn_intervals = [0  2  4  6  8.5];

projectData.calib_data.zone_angle_bound_lines = [0.7854      2.3562       3.927      5.4978];

projectData.calib_data.zone_radius_intervals = [0.0015      0.0045        0.01];

projectData.calib_data.plot_data.mu = .65;%1;

projectData.calib_data.plot_data.gamma = 0.2569;

projectData.calib_data.plot_data.alpha = 2*0.0051*0.32*projectData.calib_data.plot_data.mu;

projectData.gui_data.calib_mode = 2;

% REMOVE!
projectData.gui_data.go_above_delta_z = 0.0025;
projectData.gui_data.approach_vel = 0.0005;

%% Robot calibration

projectData.robot_calib_data.theta_v = deg2rad(linspace(0,10,4));
% projectData.robot_calib_data.theta_v = deg2rad(linspace(0,3,3));
%projectData.robot_calib_data.theta_v = 0;

%projectData.robot_calib_data.phi_v = deg2rad(0:30:(360-30));
projectData.robot_calib_data.phi_v = deg2rad(0:45:(360-45));
% projectData.robot_calib_data.phi_v = deg2rad([0 22.5:45:(360-22.5)]);
% projectData.robot_calib_data.phi_v = deg2rad(0:30:(360-30));
projectData.robot_calib_data.fn_v = ...
      -[ 0.5000    0.7000    1.0000    1.4000    1.9000    2.5000    3.2000    4.0000    4.9000    5.9000    7.0000    8.0000];
% projectData.robot_calib_data.fn_v = ...
%       -[ 0.2    1.0    2.0    3.5   5.3   6.5  7.5];


projectData.robot_calib_data.wrench_v = cell(1,length(projectData.robot_calib_data.fn_v));

max_ft = projectData.calib_data.plot_data.mu*abs(projectData.robot_calib_data.fn_v);
max_taun = projectData.calib_data.plot_data.alpha*(abs(projectData.robot_calib_data.fn_v).^(projectData.calib_data.plot_data.gamma+1));

% spherical mesh
N_sphere = 15;
[X,Y,Z] = sphere(N_sphere);
X=X(1:end-N_sphere);Y=Y(1:end-N_sphere);Z=Z(1:end-N_sphere);
angle_force_2 = pi/N_sphere;

b_rotate = false;
for fn_index=1:length(projectData.robot_calib_data.fn_v)
    
    i=1;
    projectData.robot_calib_data.wrench_v{1,fn_index}(:,end+1) = ...
            [0;0;0];
    
    while i<= length(X)
        
        fx = X(i)*max_ft(fn_index);
        fy = Y(i)*max_ft(fn_index);
        taun = Z(i)*max_taun(fn_index);
        
        if b_rotate
            ct = cos(angle_force_2); st = sin(angle_force_2);
            fxfy_rot = [ct -st; st ct] * [fx;fy];
            fx = fxfy_rot(1);
            fy = fxfy_rot(2);
        end
       
%         projectData.robot_calib_data.wrench_v{1,fn_index}(:,end+1) = ...
%             [fx;fy;taun]/2;
        projectData.robot_calib_data.wrench_v{1,fn_index}(:,end+1) = ...
            [fx;fy;taun];
        projectData.robot_calib_data.wrench_v{1,fn_index}(:,end+1) = ...
            [0;0;0];
    
        i = i + 1;
    end
    
    b_rotate = ~b_rotate;
    
end

%numcamp
N = 0;
for fn_index=1:length(projectData.robot_calib_data.fn_v)
    N = N + size(projectData.robot_calib_data.wrench_v{1,fn_index},2);
end
N = N*(length(projectData.robot_calib_data.phi_v)*(length(projectData.robot_calib_data.theta_v)-1) +1);

max_ft

max_taun


N
N*1.5/3600/24

if nargin > 0
save(filename,'projectData')
end

if nargout < 1
    figure
    hold on
   for i=1:length(projectData.robot_calib_data.fn_v)
   plot3(projectData.robot_calib_data.wrench_v{i}(1,:),projectData.robot_calib_data.wrench_v{i}(2,:),projectData.robot_calib_data.wrench_v{i}(3,:),'-*')
   end
   for i=1:length(projectData.robot_calib_data.fn_v)
   figure,plot3(projectData.robot_calib_data.wrench_v{i}(1,:),projectData.robot_calib_data.wrench_v{i}(2,:),projectData.robot_calib_data.wrench_v{i}(3,:),'-*')
   end
end

end


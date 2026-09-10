function projectData = create_empty_project(filename)
%CREATE_EMPTY_PROJECT Summary of this function goes here
%   Detailed explanation goes here

[filepath,name,ext] = fileparts(mfilename('fullpath'));
addpath(filepath);
addpath([filepath '/gui_lib']);


projectData = struct_projectData();

projectData.finger_info.finger_id = 'test';

projectData.finger_info.silicon_sphere_radius = 0.05;

projectData.calib_data.fn_intervals = [0  2  4  6  8];

projectData.calib_data.zone_angle_bound_lines = [0.7854      2.3562       3.927      5.4978];

projectData.calib_data.zone_radius_intervals = [0.0015      0.0045        0.01];

projectData.calib_data.plot_data.mu = 1;%1;

projectData.calib_data.plot_data.gamma = 0.2569;

projectData.calib_data.plot_data.alpha = 2*0.0051*0.32*projectData.calib_data.plot_data.mu;

projectData.gui_data.calib_mode = 2;

projectData.robot_calib_data.max_steps_before_compute_bias = 100;
projectData.robot_calib_data.max_steps_in_a_row = 100;
projectData.robot_calib_data.max_steps_without_save = 200;

projectData.gui_data.go_above_delta_z = 0.0025;
projectData.gui_data.approach_vel = 0.0005;

%% Robot calibration

projectData.robot_calib_data.theta_v = deg2rad(0:2.5:5);

%projectData.robot_calib_data.phi_v = deg2rad(0:30:(360-30));
projectData.robot_calib_data.phi_v = deg2rad(0:90:(360-90));

% projectData.robot_calib_data.fn_v = ...
%       -[ 0.5000    0.7000    1.0000    1.4000    1.9000    2.5000    3.2000    4.0000    4.9000    5.9000    7.0000    8.0000];
% Dft = [  0.2       0.3       0.35      0.5       0.65      0.8       0.9       0.9       1.0       1.2       1.5       1.7];
% Dtau = [ 0.0015    0.002     0.0025    0.003     0.0035    0.005     0.005     0.007     0.009     0.010     0.015     0.020]/2;

% projectData.robot_calib_data.fn_v = ...
%     -[   0.5000    0.7000    1.0000    1.4000    1.9000    2.5000    3.2000    4.0000     8.0000];
% Dft = [  0.2       0.3       0.35      0.5       0.65      0.8       0.9       0.9        1.7];
% Dtau = [ 0.0015    0.002     0.0025    0.003     0.0035    0.005     0.005     0.007      0.020]/2;

projectData.robot_calib_data.fn_v = ...
    -[   0.5000    0.7000    1.0000    1.4000    1.9000    2.5000     8.0000];
Dft = [  0.2       0.3       0.35      0.5       0.65      0.8        1.7];
Dtau = [ 0.0015    0.002     0.0025    0.003     0.0035    0.005      0.020]/2;


projectData.robot_calib_data.wrench_v = cell(1,length(projectData.robot_calib_data.fn_v));


% max_ft = [0.5000    0.7000    1.0000    1.4000    1.9000    2.5000    3.2000    4.0000    4.9000    5.9000    7.0000    8.0000];
% ft_num_points = [6     6     7     7     7     7     8    10    11    11    11    11];
% max_taun = [0.0021    0.0031    0.0049    0.0075    0.0110    0.0155    0.0212    0.0281    0.0362    0.0457    0.0567    0.0671];
% taun_num_points = [3     4     4     6     7     7     9     9     9    10     8     7];

max_ft = projectData.calib_data.plot_data.mu*abs(projectData.robot_calib_data.fn_v);
ft_num_points = ceil(2*max_ft./Dft);

max_taun = projectData.calib_data.plot_data.alpha*(abs(projectData.robot_calib_data.fn_v).^(projectData.calib_data.plot_data.gamma+1));
taun_num_points =  ceil(2*max_taun./Dtau);

for fn_index=1:length(projectData.robot_calib_data.fn_v)
    
    %check odd
    ft_num_points(fn_index) = max(ft_num_points(fn_index), 3);
    if mod(ft_num_points(fn_index),2) == 0
        ft_num_points(fn_index) = ft_num_points(fn_index) +1;
    end
    taun_num_points(fn_index) = max(taun_num_points(fn_index), 3);
    if mod(taun_num_points(fn_index),2) == 0
        taun_num_points(fn_index) = taun_num_points(fn_index) +1;
    end
    
    ft_vec = linspace(-max_ft(fn_index), max_ft(fn_index), ft_num_points(fn_index));
    taun_vec = linspace(-max_taun(fn_index), max_taun(fn_index), taun_num_points(fn_index));
    
    [FX,FY,TAUN] = meshgrid(ft_vec, ft_vec, taun_vec);
    FX=FX(:);FY=FY(:);TAUN=TAUN(:);
    
    for i=1:numel(FX)
        W_n = [FX(i)/max_ft(fn_index) FY(i)/max_ft(fn_index) TAUN(i)/max_taun(fn_index)];
        if norm(W_n) > 1
            FX(i) = nan;
            FY(i) = nan;
            TAUN(i) = nan;
        end
    end
    FX(isnan(FX)) = [];
    FY(isnan(FY)) = [];
    TAUN(isnan(TAUN)) = [];
    
    projectData.robot_calib_data.wrench_v{1,fn_index} = ...
        [ FX(:)'; FY(:)'; TAUN(:)' ];

end

%numcamp
N = 0;
for fn_index=1:length(projectData.robot_calib_data.fn_v)
    N = N + size(projectData.robot_calib_data.wrench_v{1,fn_index},2);
end
N = N*(length(projectData.robot_calib_data.phi_v)*(length(projectData.robot_calib_data.theta_v)-1) +1);

max_ft
Dft
max_taun
Dtau

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


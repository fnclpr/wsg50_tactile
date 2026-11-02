function [ calib_data ] = struct_calib_data( calib_data, delete_samples )
%GENcalib_data Summary of this function goes here
%   Detailed explanation goes here

if nargin < 1 || isempty(calib_data)
   calib_data = struct; 
end

if nargin < 2 || isempty(delete_samples)
   delete_samples = false; 
end

if ~isfield(calib_data,'fn_intervals')
    calib_data.fn_intervals = [0 2 4 6 8.5]; %[N]
end

if ~isfield(calib_data,'zone_angle_bound_lines')
    calib_data.zone_angle_bound_lines = pi*[1/4 (1/4+1/2) (1+1/4) (1+1/4+1/2)]; %[rad]
end

if ~isfield(calib_data,'zone_radius_intervals')
    calib_data.zone_radius_intervals = [0.0015, 0.0045, 0.01]; %[m]
end

%cells

%check if data are present
checkData = [ ...  
            ~isfield(calib_data,'voltage_rect_cell') ...
            ~isfield(calib_data,'time_voltage_rect_cell') ...
            ~isfield(calib_data,'voltage_raw_cell') ...
            ~isfield(calib_data,'time_voltage_raw_cell') ...
            ~isfield(calib_data,'wrench_cell') ...
            ~isfield(calib_data,'time_wrench_cell') ...
            ~isfield(calib_data,'pose_cell') ...
            ~isfield(calib_data,'time_pose_cell')];
if ~delete_samples && (sum(checkData) ~= length(checkData) && sum(checkData) ~= 0)
	error('finger_calib_gui:bad_data','BAD STRUCT DATA')
end

if (sum(checkData) == length(checkData)) || delete_samples   
    
    num_zones = compute_num_zones(calib_data.zone_angle_bound_lines, calib_data.zone_radius_intervals);
    
    size_cell = [num_zones,length(calib_data.fn_intervals)-1];
    
    calib_data.voltage_rect_cell = cell(size_cell);
    calib_data.time_voltage_rect_cell = cell(size_cell);
    calib_data.voltage_raw_cell = cell(size_cell);
    calib_data.time_voltage_raw_cell = cell(size_cell);
    calib_data.wrench_cell = cell(size_cell);
    calib_data.time_wrench_cell = cell(size_cell);
    calib_data.pose_cell = cell(size_cell);  
    calib_data.time_pose_cell = cell(size_cell);
    
    if ~isfield(calib_data,'plot_data')
        calib_data.plot_data = struct;
    end
    calib_data.plot_data = struct_plot_data(calib_data.plot_data, size_cell); %struct ex-novo
   
else
    if ~isfield(calib_data,'plot_data')
        error('finger_calib_gui:bad_data','plot data not present!')
    end
end

end


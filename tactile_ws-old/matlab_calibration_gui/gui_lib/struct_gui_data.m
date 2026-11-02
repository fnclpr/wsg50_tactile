function [ gui_data ] = struct_gui_data( gui_data )
%GENUSERDATA Summary of this function goes here
%   Detailed explanation goes here

if nargin < 1 || isempty(gui_data)
   gui_data = struct; 
end

if ~isfield(gui_data,'calib_mode')
    gui_data.calib_mode = 2; % 0:None, 1:HandCalib, 2:RobotCalib
end

if ~isfield(gui_data,'min_fz') %only for HandCalib Mode
    gui_data.min_fz = 0.2;
end

if ~isfield(gui_data,'dim_sample_buffer')
    gui_data.dim_sample_buffer = 50;
end

end


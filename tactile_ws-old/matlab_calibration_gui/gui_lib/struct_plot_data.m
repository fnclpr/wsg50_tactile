function [ plot_data ] = struct_plot_data( plot_data, size_cell )
%GENUSERDATA Summary of this function goes here
%   Detailed explanation goes here

if nargin < 1 || isempty(plot_data)
   plot_data = struct; 
end

if ~isfield(plot_data,'mu')
    plot_data.mu = 1;
end

if ~isfield(plot_data,'gamma')
    plot_data.gamma = 0.2569;
end

if ~isfield(plot_data,'alpha')
    plot_data.alpha = 2*0.0051*0.32*plot_data.mu;
end

plot_data.wrench_plot_cell = cell(size_cell);
    
end


function [ projectData, dependent_data ] = struct_projectData( projectData, delete_samples )
%GENUSERDATA create or update a project data struct
%   create a project data struct adding struct elements if not defined
% if nargout=2 return a struct of dependent_data

VERSION = 3;

if nargin < 1 || isempty(projectData)
   projectData = struct; 
end

if nargin < 2 || isempty(delete_samples)
   delete_samples = false; 
end

if ~isfield(projectData,'version')
    projectData.version = VERSION;
end

if projectData.version~=VERSION
    warning('finger_calib_gui:bad_version', 'The input project has a bad version id, found %d expected %d', projectData.version, VERSION);
end

if ~isfield(projectData,'finger_info')
    projectData.finger_info = struct;
end
projectData.finger_info = struct_finger_info(projectData.finger_info);

if ~isfield(projectData,'calib_data')
    projectData.calib_data = struct;
end
projectData.calib_data = struct_calib_data(projectData.calib_data, delete_samples);

if ~isfield(projectData,'gui_data')
    projectData.gui_data = struct;
end
projectData.gui_data = struct_gui_data(projectData.gui_data);

if ~isfield(projectData,'robot_calib_data')
    projectData.robot_calib_data = struct;
end
projectData.robot_calib_data = struct_robot_calib_data(projectData.robot_calib_data);

if nargout > 1
    dependent_data = compute_dependent_data(projectData);
end

end


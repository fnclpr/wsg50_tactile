function [  voltages_rect, time_voltages_rect, ...
            voltages_raw, time_voltages_raw, ...
            wrenches, time_wrenches, ...
            poses, time_poses ...
            ] = mergeCalibData(calib_data , b_sort_voltages_rect)
        
    if nargin < 2 || isempty(b_sort_voltages_rect)
        b_sort_voltages_rect = false;
    end
    
    %Merge all
    voltages_rect = [];
    time_voltages_rect = [];
    voltages_raw = [];
    time_voltages_raw = [];
    wrenches = [];
    time_wrenches = [];
    poses = [];
    time_poses = [];

    for i = 1:(size(calib_data.voltage_rect_cell,1)*size(calib_data.voltage_rect_cell,2))
        voltages_rect = [voltages_rect calib_data.voltage_rect_cell{i}]; %#ok<*AGROW>
        time_voltages_rect =  [time_voltages_rect calib_data.time_voltage_rect_cell{i}];
        voltages_raw = [voltages_raw calib_data.voltage_raw_cell{i}];
        time_voltages_raw = [time_voltages_raw calib_data.time_voltage_raw_cell{i}];
        wrenches = [wrenches calib_data.wrench_cell{i}];   
        time_wrenches = [time_wrenches calib_data.time_wrench_cell{i}];
        poses = [poses calib_data.pose_cell{i}];   
        time_poses = [time_poses calib_data.time_pose_cell{i}];
    end

    %sort
    if(b_sort_voltages_rect)
        [~, sorted_indx] = sort(time_voltages_rect);
    else
        [~, sorted_indx] = sort(time_wrenches);
    end
    
    voltages_rect = voltages_rect(:,sorted_indx);
    time_voltages_rect = time_voltages_rect(sorted_indx);
    voltages_raw = voltages_raw(:,sorted_indx);
    time_voltages_raw = time_voltages_raw(sorted_indx);
    wrenches = wrenches(:,sorted_indx);
    time_wrenches = time_wrenches(sorted_indx);
    poses = poses(:,sorted_indx);
    time_poses = time_poses(sorted_indx);
    
end

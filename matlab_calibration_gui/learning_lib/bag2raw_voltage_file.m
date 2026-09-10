function bag2raw_voltage_file(bag_file,output_file, topic_name)
% BAG2FILE transform a .bag file in .mat file. Use it to store the ZERO raw
% voltages in a matlab file

if nargin < 3
    topic_name = '/tactile_voltage_raw_filter';
end

%% Add path
addpath([userpath '/read_bag_functions']);

%% Load Bag file

if ~endsWith(bag_file,'.bag','IgnoreCase',true)
    bag_file = [bag_file '.bag'];
end
myBag = ros.Bag.load(bag_file);

[time_voltages_raw, voltages_raw] = readTactileStamped(myBag, topic_name );

save(output_file, 'time_voltages_raw', 'voltages_raw')

end


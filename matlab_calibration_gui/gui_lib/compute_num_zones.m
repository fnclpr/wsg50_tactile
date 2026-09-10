function num_zones = compute_num_zones(zone_angle_bound_lines,zone_radius_intervals)
%COMPUTE_NUM_ZONES Summary of this function goes here
%   Detailed explanation goes here

num_zones = 1+length(zone_angle_bound_lines)*(length(zone_radius_intervals)-1);

end


function zone_index = find_geometric_zone(centroid,angle_bound_lines, zone_radius_intervals)

[theta,rho] = cart2pol(centroid(1),centroid(2));
theta = wrapTo2Pi(theta);

rho_index = find_interval([-1 zone_radius_intervals],rho);
if isnan(rho_index)
    zone_index = nan;
    return;
elseif rho_index == 1
    zone_index = 1;
    return;
end

theta_index = find_interval(angle_bound_lines,theta)+1;
if isnan(theta_index)
    theta_index = 1;
end

zone_index = (rho_index-2)*length(angle_bound_lines)+theta_index+1;


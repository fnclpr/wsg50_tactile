function central_angles = compute_central_angles(angle_intervals)
% compute the central angles from a given interval

angle_intervals = wrapTo2Pi(angle_intervals);
central_angles = zeros(1,length(angle_intervals)-1);
for i=1:(length(angle_intervals)-1)
    central_angles(i) = (angle_intervals(i) + angle_intervals(i+1))/2;
end

central_angles = [ wrapTo2Pi((angle_intervals(1)+2*pi + angle_intervals(end))/2) central_angles];

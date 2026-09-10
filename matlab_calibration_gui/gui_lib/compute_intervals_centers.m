function intervals_centers = compute_intervals_centers(intervals)
% compute the centers of given intervals

intervals_centers = zeros(1,length(intervals)-1);
for i=1:(length(intervals)-1)
    intervals_centers(i) = (intervals(i) + intervals(i+1))/2;
end


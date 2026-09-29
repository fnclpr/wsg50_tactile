# Output of tactile_core.processing applied to one debiased tactile
# frame: centroid, geometric zone, and limit-surface plot point. This
# is what the monitor GUI's centroid map and unit-sphere plot subscribe
# to (Steps 7/14 of the project plan).
#
# Produced from:
#   tactile_core.processing.centroid.compute_centroid
#   tactile_core.processing.zoning.find_geometric_zone
#   tactile_core.processing.limit_surface.compute_wrench_plot_point

std_msgs/Header header

# Contact centroid on the tactile map, in meters, sensor frame.
geometry_msgs/Point centroid

# 1-indexed geometric zone (matches tactile_core.processing.zoning's
# MATLAB-compatible convention: zone 1 = central zone). -1 is the
# sentinel for "outside the calibrated area" -- Python NaN has no
# clean equivalent in a ROS2 integer field.
int32 zone_index

# [ft_x*, ft_y*, taun*]: limit-surface-normalized plot point, see
# compute_wrench_plot_point. All three values are dimensionless
# (normalized by the per-zone/per-fn-bin ftmax/taunmax).
float64[3] limit_surface_point

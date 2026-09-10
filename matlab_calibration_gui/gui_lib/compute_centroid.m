function centroid = compute_centroid(voltages, taxels_x_coords, taxels_y_coords, broken_cells)

if nargin > 3
    voltages(broken_cells) = 0;
end

sumV = sum(voltages(:));
if any( abs(voltages) > 0.01 ) 
    voltages_matrix = reshape(voltages,5,5)';

    x = sum(sum(voltages_matrix.*taxels_x_coords))/sumV;
    y = sum(sum(voltages_matrix.*taxels_y_coords))/sumV;
else
    x = 0;
    y = 0;
end

centroid = [x;y];




function wrench_plot_point = compute_wrench_plot_point(wrench,fz_nominal,transform_of_central_zone, param_mu, param_alpha, param_gamma)
%COMPUTE_PLOT_POINT Compute the plot point for the gui
%   Detailed explanation goes here


wrench_transformed = transform_wrench(transform_of_central_zone,wrench);

contact_fn_nominal = transform_of_central_zone(3,3)*fz_nominal; %transform the vector [0;0;fz]

max_ft_nominal = compute_max_ft(contact_fn_nominal, param_mu);
max_taun_nominal = compute_max_taun(contact_fn_nominal, param_alpha, param_gamma);
wrench_plot_point = [wrench_transformed(1:2)/max_ft_nominal; wrench_transformed(end)/max_taun_nominal];
                                   
end


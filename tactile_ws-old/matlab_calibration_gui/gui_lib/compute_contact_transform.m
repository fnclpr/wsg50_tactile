function  cont_T_sc = compute_contact_transform(centroid, silicon_sphere_radius, z_coord_sphere_frame_wrt_calib_sensor_frame)
    %compute the a transform of calib frame wrt contact frame

    sf_P_cont = [ centroid(1) ; centroid(2); sqrt( (silicon_sphere_radius^2) - (centroid(1)^2) - (centroid(2)^2) ) ];
    
    n_hat = sf_P_cont/silicon_sphere_radius;
    
    sc_x_cont = [1;0;0] - n_hat(1)*n_hat;
    sc_x_cont = sc_x_cont/norm(sc_x_cont);
    sc_y_cont = [0;1;0] - n_hat(2)*n_hat;
    sc_y_cont = sc_y_cont/norm(sc_y_cont);
    
    sc_R_cont = [ sc_x_cont , sc_y_cont , n_hat];
    
    sc_T_sf = [ eye(3) , [0 ; 0 ; z_coord_sphere_frame_wrt_calib_sensor_frame] ; [0 0 0 1] ];
    
    sc_P_cont_tilde = sc_T_sf * [sf_P_cont ; 1];
    
    sc_T_cont = [ [ sc_R_cont ; [0 0 0] ] ,  sc_P_cont_tilde ];
    
    cont_T_sc = inv(sc_T_cont);
end
function success = ROS_service_call_set_spherical_coords(service_client, rho, theta, phi)
%ROS_service_call_set_bool call a set bool ros server

req = service_client.rosmessage;
req.Rho = rho;
req.Theta = theta;
req.Phi = phi;

res = service_client.call(req, 'Timeout', 10);

success = res.Success;

if ~success
    warning('sun_tactile_calibration:service_client_error','Error on service client %s\n\tmsg: %s', service_client.ServiceName, res.Message)
end

end


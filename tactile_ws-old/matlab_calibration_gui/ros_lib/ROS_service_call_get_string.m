function out = ROS_service_call_get_string(service_client)
%ROS_service_call_set_bool call a set bool ros server

req = service_client.rosmessage;

res = service_client.call(req, 'Timeout', 10);

out = res.Status;

end


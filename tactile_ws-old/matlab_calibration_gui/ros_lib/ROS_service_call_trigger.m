function [success, msg] = ROS_service_call_trigger(service_client)
%ROS_service_call_trigger call a trigger ros server

req = service_client.rosmessage;

res = service_client.call(req, 'Timeout', 10);

success = res.Success;
msg = res.Message;

if ~success
    warning('sun_tactile_calibration:service_client_error','Error on service client %s\n\tmsg: %s', service_client.ServiceName, res.Message)
end

end


function t_wrench = transform_wrench(t_T_s, s_wrench )
% transform a wrench, t=target frame, s=source frame

t_wrench = zeros(6,1);

t_wrench(1:3) = t_T_s(1:3,1:3) * s_wrench(1:3);
t_wrench(4:6) = t_T_s(1:3,1:3) * s_wrench(4:6) + cross(t_T_s(1:3,4) ,t_wrench(1:3));

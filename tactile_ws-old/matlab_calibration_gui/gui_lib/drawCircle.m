function drawCircle(ax, r)
%DRAWCIRCLE Summary of this function goes here
%   Detailed explanation goes here

%// center
c = [0 0];

pos = [c-r 2*r 2*r];
rectangle(ax,'Position',pos,'Curvature',[1 1])


end


function drawUnitSphere(ax)
%DRAWCIRCLE Summary of this function goes here
%   Detailed explanation goes here

[xs,ys,zs] = sphere(100);
hs = surf(ax,xs,ys,zs);
shading(ax, 'interp')
colormap(ax , 'summer')
alpha(hs,0.2);

end


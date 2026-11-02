function h = plotLinePolar(ax, rho, ang)
%PLOTLINEPOLAR Summary of this function goes here
%   Detailed explanation goes here

[X,Y] = pol2cart(ang,rho);

h = plot(ax,X,Y,'k');

end


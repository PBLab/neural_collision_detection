x = [0.1, 0, 0, 1, 0, 0, -1]';
y = [-0.1, -1, 0, 0, 0, 1, 0]';
t = tiledlayout(1,2);
t.TileSpacing = 'compact';
t.Padding = 'compact';
ax1 = nexttile;
shp = alphaShape(x, y);
plot(shp);
hold on
title(shp.Alpha);
scat_points(x, y, ax1);
spec =  alphaSpectrum(shp);
shp.Alpha = spec(1);
ax2 = nexttile;
plot(shp);
hold on
title(shp.Alpha);
scat_points(x, y, ax2);


function scat_points(x, y, a)
%SCAT_POINTS Scatterplot on the current figure with pre-defined settings
    scatter(a, x(2:end), y(2:end), 140, 'k', 'filled')
    hold on
    scatter(a, x(1), y(1), 140, 'r', 'filled')
    a.PlotBoxAspectRatio = [1, 1, 1];
    a.FontSize = 28;


end
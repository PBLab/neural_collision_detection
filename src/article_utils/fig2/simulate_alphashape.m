points = [0, 0, 1; -1, 0, 0; 1, 0, 0; 0, 1, 0; 0, -1, 0; 0, 0, 0; 0.25, 0.25, 0; -0.25, 0.25, 0; 0.25, -0.25, 0; -0.25, -0.25, 0];
shp = alphaShape(points, Inf);
crit = criticalAlpha(shp, 'one-region');
spec = shp.alphaSpectrum;
all_boundaries = shp.boundaryFacets;
all_boundaries = union(union(all_boundaries(:, 1), all_boundaries(:, 2)), all_boundaries(:, 3));
all_verts = 1:length(points);
points_inside = setdiff(all_verts, all_boundaries);
plot(shp)
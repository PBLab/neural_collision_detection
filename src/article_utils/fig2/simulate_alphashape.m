%% Simplistic simulation
points = [0, 0, 1; -1, 0, 0; 1, 0, 0; 0, 1, 0; 0, -1, 0; 0, 0, 0; 0.25, 0.25, 0; -0.25, 0.25, 0; 0.25, -0.25, 0; -0.25, -0.25, 0];
shp = alphaShape(points, Inf);
crit = criticalAlpha(shp, 'one-region');
spec = shp.alphaSpectrum;
all_boundaries = shp.boundaryFacets;
all_boundaries = union(union(all_boundaries(:, 1), all_boundaries(:, 2)), all_boundaries(:, 3));
all_verts = 1:length(points);
points_inside = setdiff(all_verts, all_boundaries);
plot(shp)

%% Sim based on real neuron
foldername = '/data/neural_collision_detection/data/neurons/';
folder_with_glob = strcat(foldername, '*.csv');
all_files = dir(folder_with_glob)';
filenames = extract_neuron_names_from_fname(all_files);
file = strcat(foldername, filenames{2});
alpha = 0.187030894655284;
neuron = read_neuron_data(file);
shape = alphaShape(neuron);
shape.Alpha = alpha;
plot(shape)
hold on
scatter3(neuron(:, 1), neuron(:, 2), neuron(:, 3), 'y.')
points_inside = inShape(shape, neuron(:, 1), neuron(:, 2), neuron(:, 3));
sum(points_inside)
scatter3(neuron(points_inside, 1), neuron(points_inside, 2), neuron(points_inside, 3), 'ro');

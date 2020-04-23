%% Simplistic simulation
points = [0, 0, 1; -1, 0, 0; 1, 0, 0; 0, 1, 0; 0, -1, 0; 0, 0, 0; 0.25, 0.25, 0; -0.25, 0.25, 0; 0.25, -0.25, 0; -0.25, -0.25, 0];
shp = alphaShape(points, Inf);
crit = criticalAlpha(shp, 'one-region');
spec = shp.alphaSpectrum;
% all_boundaries = shp.boundaryFacets;
% all_boundaries = union(union(all_boundaries(:, 1), all_boundaries(:, 2)), all_boundaries(:, 3));
% all_verts = 1:length(points);
% points_inside = setdiff(all_verts, all_boundaries);
plot(shp, 'FaceColor', 'k', 'FaceAlpha', 0.3)
shp.Alpha = crit;
hold on
plot(shp, 'FaceColor', 'magenta', 'FaceAlpha', 0.1)
hold on
scatter3(points(:, 1), points(:, 2), points(:, 3), 150, '*');

%% Show algorithm's result for mock data
is_hidden = uint8(zeros(length(points), 1));
alphas = [Inf, crit];
alphas_str = string(alphas);
shape = alphaShape(points);
collisions_with_all_alphas = create_collision_table(alphas, [length(points), 2]);
alpha_str = collisions_with_all_alphas.Properties.VariableNames;
for alpha_num = 1:length(alphas)
    shape.Alpha = alphas(alpha_num);
    rows_of_hidden_colls = find_hidden_collisions(shape, points);
    is_hidden(rows_of_hidden_colls) = uint8(1);
    collisions_with_all_alphas.(alphas_str(alpha_num)) = is_hidden;
    is_hidden(:) = uint8(0);
end
hiddenness = sum(collisions_with_all_alphas.Variables, 2);

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

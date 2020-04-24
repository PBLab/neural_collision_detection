function [neural_points] = read_neuron_data(neuron_fname)
% Read the neuronal data from the given filename.
% Returns a matrix with three columns  (x-y-z) with the number
% of rows as the number of collisions.

neural_points = readmatrix(neuron_fname);
neural_points = neural_points(:, 1:3);
end


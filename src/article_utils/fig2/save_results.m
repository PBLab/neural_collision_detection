function save_results(first_alpha_per_point, neuron_name)
% Save the given results to a folder
    foldername = '/data/neural_collision_detection/results/2020_02_14/';
    filename = strcat(foldername, neuron_name, '_alpha_values.mat');
    save(filename, 'first_alpha_per_point');
end


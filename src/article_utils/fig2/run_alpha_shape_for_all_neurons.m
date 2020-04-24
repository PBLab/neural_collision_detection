% This is the main script for running the alpha shapes analysis.
% For each neuron it finds a list of alpha values that generate different
% shapes and see which point on the neuron takes part in creating the
% boundary of that alpha shape. The result is an array that contains
% information on the value of the first viable alpha parameter for each
% point on the neuron.

foldername = '/data/neural_collision_detection/data/neurons/';
folder_with_glob = strcat(foldername, '*.csv');
all_files = dir(folder_with_glob)';
neuron_names = extract_neuron_names_from_fname(all_files);
all_shapes = cell(length(all_files), 1);
parfor filenum = 1:length(all_files)
    file = strcat(foldername, neuron_names{filenum});
    hiddenness = find_neuron_alpha_shapes(file, neuron_names{filenum});
    all_shapes{filenum} = hiddenness;
end
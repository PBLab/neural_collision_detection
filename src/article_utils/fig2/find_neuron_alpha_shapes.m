function first_alpha_per_point = find_neuron_alpha_shapes(fname, neuron_name)
% Find the first alpha-shape value which includes all neural points for a
% variety of different alpha values. This functions constructs many
% different alpha shapes with different alpha values, and then check
% whether each collision is located inside that newly-generated alpha
% shape.
    neuron = read_neuron_data(fname);
    shape = alphaShape(neuron);
    alphas = get_alpha_values_to_process(shape);
    table_size = [size(neuron, 1), size(alphas, 1)];
    collisions_with_all_alphas = create_collision_table(alphas, table_size);
    is_hidden = ~logical(1:length(neuron))';
    % We iterate over VariableNames and not directly over the alpha values
    % since a bug caused the final table to have more than the pre-set
    % number of columns in it.
    for alpha = collisions_with_all_alphas.Properties.VariableNames
        shape.Alpha = str2double(alpha{1});
        rows_of_hidden_colls = find_hidden_collisions(shape, neuron);
        is_hidden(rows_of_hidden_colls) = true;
        collisions_with_all_alphas.(alpha{1}) = is_hidden;
        is_hidden(:) = false;
    end
    [first_alpha_index_per_point, never_on_boundary] = find_first_alpha(collisions_with_all_alphas);
    first_alpha_per_point = get_first_alpha_per_point(first_alpha_index_per_point, never_on_boundary, alphas);
    save_results(first_alpha_per_point, neuron_name);
end
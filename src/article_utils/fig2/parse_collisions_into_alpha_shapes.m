function first_alpha_per_collision = parse_collisions_into_alpha_shapes()
% Find the first alpha-shape value which includes all collisions for a
% variety of different alpha values. This functions constructs many
% different alpha shapes with different alpha values, and then check
% whether each collision is located inside that newly-generated alpha
% shape.
    fname = '/data/neural_collision_detection/results/2020_02_14/normalized_agg_results_AP130312_s1c1_thresh_0.mat';
    collisions = read_collision_data(fname);
    shape = alphaShape(collisions);
    alphas = flip(shape.alphaSpectrum);
    samples = uint32(linspace(1, length(alphas), 1000));
    alphas = alphas(samples);
    table_size = [size(collisions, 1), size(alphas, 1)];
    collisions_with_all_alphas = create_collision_table(alphas, table_size);
    is_hidden = ~logical(1:length(collisions))';
    % We iterate over VariableNames and not directly over the alpha values
    % since a bug caused the final table to have more than the pre-set
    % number of columns in it.
    for alpha = collisions_with_all_alphas.Properties.VariableNames
        shape.Alpha = str2double(alpha{1});
        rows_of_hidden_colls = find_hidden_collisions(shape, length(collisions));
        is_hidden(rows_of_hidden_colls) = true;
        collisions_with_all_alphas.(alpha{1}) = is_hidden;
        is_hidden(:) = false;
    end
    first_alpha_per_collision = find_first_alpha(collisions_with_all_alphas);
    first_alpha_per_collision = alphas(first_alpha_per_collision);
end
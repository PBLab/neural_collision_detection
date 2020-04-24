function table_ = create_collision_table(alphas, table_size)
%Creates a table data structure with the given number of rows and columns.
    table_columns = string(alphas);
    var_types = string(alphas);
    [~, uniques, all_idx] = unique(table_columns);
    dups = setdiff(all_idx, uniques);
    if ~isempty(dups)
        for dup = dups
           table_columns{dup} = strcat(table_columns{dup}, '1'); 
        end
    end
    var_types(:) = 'uint8';
    table_ = table('Size', table_size, 'VariableTypes', var_types, 'VariableNames', table_columns); 
end


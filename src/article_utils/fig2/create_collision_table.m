function table_ = create_collision_table(alphas, table_size)
%Creates a table data structure with the given number of rows and columns.
    table_columns = string(alphas);
    var_types = string(alphas);
    var_types(:) = 'logical';
    table_ = table('Size', table_size, 'VariableTypes', var_types, 'VariableNames', table_columns); 
end


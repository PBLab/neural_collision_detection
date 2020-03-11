function first_alpha = find_first_alpha(coll_table)
%Finds the first alpha value which had the collision on the boundary.
%   For each of the collisions find the minimal alpha value that included
%   that collision in the boundary of the alpha shape. Returns an array
%   with the length of the given table, with its values being the index to
%   the alpha value columns that we should use.
    colls = table2array(coll_table);
    first_alpha = zeros(size(colls, 1), 1);
    for row = 1:length(colls)
        [~, column] = find(colls(row, :));
        if size(column, 2) > 0
            first_alpha(row) = column(1); 
        end
    end

end

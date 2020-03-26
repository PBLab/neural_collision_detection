function hidden_collisions = find_hidden_collisions(shape, colls)
%Finds all collisions which aren't on the border of the given alpha shape.
%   This function receives an alpha shape with a pre-determined alpha
%   value, and should find the collisions which do not create the
%   boundaries of that alpha shape, meaning that they're hidden inside it.
%   It returns the row numbers of these collisions.
    boundaries = shape.boundaryFacets;
    inside = inShape(shape, colls);
    colls_index = (1:length(colls))';
    inside = colls_index(inside);
    hidden_collisions = setdiff(inside, boundaries);    
end


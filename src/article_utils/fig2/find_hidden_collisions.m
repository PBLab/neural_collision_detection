function hidden_collisions = find_hidden_collisions(shape, points)
%Finds all points which aren't on the border of the given alpha shape.
%   This function receives an alpha shape with a pre-determined alpha
%   value, as well as all points for that shape,  and should find the 
%   collisions which do not create the boundaries of that alpha shape, 
%   meaning that they're hidden inside it. It returns the row numbers of 
%   these points.

    % The first phase is to get all boundary facets as coordinates. We'll
    % then feed them into a convex hull (simplified) function that will
    % generate the minimal surface that creates the same . We can't use
    % an Alpha shape with an Inf alpha value since it doesn't have the
    % simplify option, which reduces the needed number of points at the
    % edges.
    [faces, vertices] = shape.boundaryFacets;
    in = inpolyhedron(faces, vertices, points);
    boundary_vertices = unique(faces);
    index = 1:length(points);
    in = index(in);
    hidden_collisions = setdiff(in, boundary_vertices);
end


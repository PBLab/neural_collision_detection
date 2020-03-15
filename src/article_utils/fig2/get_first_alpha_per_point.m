function first_alpha_per_point = get_first_alpha_per_point(first_index, never_on_boundary, alphas)
% Find the largest alpha value that includes each collision in its boundary
% shape.
%   For each collision find the largest alpha value which first includes
%   this coordinates in a boundary facet of the alpha shape. First index
%   are the indices into the alpha parameter values, never_on_boundary is
%   an array pointing to collisions which were never found to be on a
%   boundary, and alphas is the actual array of alpha parameter values.
    first_index(never_on_boundary) = 1;
    first_index = uint32(first_index);
    first_alpha_per_point = alphas(first_index);
    first_alpha_per_point(never_on_boundary) = 0;
end


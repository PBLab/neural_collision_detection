function [collisions] = read_collision_data(collision_fname)
% Read the collision data from the given filename.
% Returns a matrix with three columns  (x-y-z) with the number
% of rows as the number of collisions.

collisions = double(load(collision_fname).unique_coords);
end


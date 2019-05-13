function write_mesh_to_disk(M_surf, M_caps, offsetXYZ, fname)
faces = [M_surf.faces; M_caps.faces];
vertices = [M_surf.vertices; M_caps.vertices];
csv_fname = strcat(fname(1:end-3), 'csv');
vert_fname = strcat('vertices_', csv_fname);
faces_fname = strcat('faces_', csv_fname);

dlmwrite(vert_fname, bsxfun(@minus, vertices, offsetXYZ), 'precision', 7);
dlmwrite(faces_fname, faces, 'precision', 7);
end
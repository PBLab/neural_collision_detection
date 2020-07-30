function batch_ctp2mesh2disk(folder)
% Convert all .mat files in the folder to meshes.

folder_with_glob = fullfile(folder, '*.mat');
files = dir(folder_with_glob);

for filenum = 1:length(files)
    full_fname = fullfile(files(filenum).folder, files(filenum).name);
    [M_surf,M_caps,offsetXYZ] = ctp2mesh(full_fname);
    new_name = strcat(files(filenum).name(1:end-4), '_yz_flipped.csv');
    write_mesh_to_disk(M_surf, M_caps, offsetXYZ, new_name);
end
end
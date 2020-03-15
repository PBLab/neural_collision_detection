function [filenames] = extract_neuron_names_from_fname(all_files)
%Extract the neurons' names from the given dir content
    filenames = cell(length(all_files), 1);
    for filenum = 1:length(all_files)
        filename_with_ext = all_files(filenum).name;
        filenames{filenum, 1} = filename_with_ext(1:end-4);
    end
end

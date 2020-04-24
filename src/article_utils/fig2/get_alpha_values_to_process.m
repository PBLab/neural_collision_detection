function alphas = get_alpha_values_to_process(shape)
%Generates all relevant alpha values that we'll work with during this
%script.
    alphas = fliplr(shape.alphaSpectrum);
    alphas(1) = alphas(1) + 0.00000001;
    samples = 1:min(10000, size(alphas, 1));
    alphas = unique(alphas(samples));
    diffs = diff(alphas);
    [m, i] = min(diffs);
    if m < 1e-5
        alphas(i) = alphas(i) - 1e-5;
        alphas(i+1) = alphas(i + 1) + 1e-5;
    end
end
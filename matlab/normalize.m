function normalize()
%NORMALIZE  Min-max scale every column of the edited dataset to [-1, 1].
%
% This matches the original thesis pipeline (Eq. 3-1 and 3-2). The label
% column is already in {-1, +1}, so it is unchanged by the transform.

    root = fileparts(fileparts(mfilename('fullpath')));
    inPath = fullfile(root, 'data', 'processed', 'dataset2_edited.csv');
    outPath = fullfile(root, 'data', 'processed', 'dataset3_normalized.csv');

    data = readmatrix(inPath);
    lb = -1;
    ub = 1;

    colMin = min(data, [], 1);
    colMax = max(data, [], 1);
    span = colMax - colMin;
    span(span == 0) = 1;

    scaled = (data - colMin) ./ span;
    scaled = (ub - lb) * scaled + lb;

    writematrix(scaled, outPath);
    fprintf('Wrote %d x %d normalized matrix to %s\n', size(scaled, 1), size(scaled, 2), outPath);
end

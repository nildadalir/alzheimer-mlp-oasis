function split_data()
%SPLIT_DATA  Hold out 10% of rows for testing (90/10, matching the thesis).
%
% The original script called dividerand(Q, 0.9, 0.1) with two outputs. That
% API expects (train, validation, test) ratios, so MATLAB treated 0.1 as the
% validation share, applied the default 0.15 test share, and returned the
% validation indices as "test". The leftover 13% of rows were discarded.
% This version uses a true 90/10 split and keeps every row.

    root = fileparts(fileparts(mfilename('fullpath')));
    inPath = fullfile(root, 'data', 'processed', 'dataset3_normalized.csv');
    trainPath = fullfile(root, 'data', 'processed', 'dataset4_train.csv');
    testPath = fullfile(root, 'data', 'processed', 'dataset5_test.csv');

    rng(42);
    X = readmatrix(inPath);
    n = size(X, 1);

    [trainInd, ~, testInd] = dividerand(n, 0.9, 0.0, 0.1);

    writematrix(X(trainInd, :), trainPath);
    writematrix(X(testInd, :), testPath);
    fprintf('Train: %d rows -> %s\n', numel(trainInd), trainPath);
    fprintf('Test:  %d rows -> %s\n', numel(testInd), testPath);
end

function metrics = mlp_classifier(varargin)
%MLP_CLASSIFIER  Train and evaluate a 9-8-4-1 feedforward network.
%
% Optional name-value arguments:
%   'DropFeatures'  vector of column indices in the *feature* matrix to drop
%                   (1=Sex ... 9=ASF). Example: [7 9] drops eTIV and ASF.
%   'ShowWindow'    true/false, MATLAB nntraintool window (default true)

    p = inputParser;
    addParameter(p, 'DropFeatures', [], @(x) isnumeric(x));
    addParameter(p, 'ShowWindow', true, @(x) islogical(x) || isnumeric(x));
    parse(p, varargin{:});
    dropFeatures = p.Results.DropFeatures;
    showWindow = logical(p.Results.ShowWindow);

    root = fileparts(fileparts(mfilename('fullpath')));
    trainPath = fullfile(root, 'data', 'processed', 'dataset4_train.csv');
    testPath = fullfile(root, 'data', 'processed', 'dataset5_test.csv');

    trainData = readmatrix(trainPath);
    testData = readmatrix(testPath);

    train_y = trainData(:, 1)';
    train_x = trainData(:, 2:end)';
    test_y = testData(:, 1)';
    test_x = testData(:, 2:end)';

    if ~isempty(dropFeatures)
        train_x(dropFeatures, :) = [];
        test_x(dropFeatures, :) = [];
    end

    fprintf('MLP: %d train samples, %d test samples, %d inputs\n', ...
        size(train_x, 2), size(test_x, 2), size(train_x, 1));

    hiddenSizes = [8, 4];
    rng(42);

    tic;
    if exist('feedforwardnet', 'file')
        net = feedforwardnet(hiddenSizes, 'trainlm');
        net.divideFcn = 'dividetrain';  % do not re-split the already-held-out data
        net.trainParam.showWindow = showWindow;
        net = train(net, train_x, train_y);
        scores = net(test_x);
    else
        net = newff(train_x, train_y, hiddenSizes);
        net = train(net, train_x, train_y);
        scores = sim(net, test_x);
    end
    trainTime = toc;

    tic;
    pred = ones(size(scores));
    pred(scores < 0) = -1;
    testTime = toc;

    % Standard confusion-matrix labels (positive class = Demented = +1)
    TP = sum(pred == 1  & test_y == 1);
    TN = sum(pred == -1 & test_y == -1);
    FP = sum(pred == 1  & test_y == -1);  % predicted demented, actually healthy
    FN = sum(pred == -1 & test_y == 1);   % predicted healthy, actually demented

    n = TP + TN + FP + FN;
    accuracy = (TP + TN) / n;
    precision = safe_div(TP, TP + FP);
    recall = safe_div(TP, TP + FN);
    specificity = safe_div(TN, TN + FP);
    f1 = safe_div(2 * precision * recall, precision + recall);

    metrics = struct('TP', TP, 'TN', TN, 'FP', FP, 'FN', FN, ...
        'accuracy', accuracy, 'precision', precision, 'recall', recall, ...
        'specificity', specificity, 'f1', f1, ...
        'trainTime', trainTime, 'testTime', testTime, ...
        'perSampleUs', (testTime / numel(pred)) * 1e6);

    fprintf('TP=%d  TN=%d  FP=%d  FN=%d\n', TP, TN, FP, FN);
    fprintf('accuracy=%.6f\n', accuracy);
    fprintf('precision=%.6f\n', precision);
    fprintf('recall=%.6f\n', recall);
    fprintf('specificity=%.6f\n', specificity);
    fprintf('f1=%.6f\n', f1);
    fprintf('train_time=%.4f s   test_time=%.4f s\n', trainTime, testTime);
end

function y = safe_div(a, b)
    if b == 0
        y = 0;
    else
        y = a / b;
    end
end

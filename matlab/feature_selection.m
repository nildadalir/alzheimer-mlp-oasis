function feature_selection()
%FEATURE_SELECTION  Rank predictors with MRMR (minimum redundancy, maximum relevance).
%
% Requires the Statistics and Machine Learning Toolbox (fscmrmr).

    root = fileparts(fileparts(mfilename('fullpath')));
    inPath = fullfile(root, 'data', 'processed', 'dataset3_normalized.csv');
    resultsDir = fullfile(root, 'results');
    if ~exist(resultsDir, 'dir')
        mkdir(resultsDir);
    end

    data = readmatrix(inPath);
    y = data(:, 1);
    X = data(:, 2:end);
    names = {'Sex', 'Age', 'EDUC', 'SES', 'MMSE', 'CDR', 'eTIV', 'nWBV', 'ASF'};

    [idx, scores] = fscmrmr(X, y);

    fprintf('\nMRMR ranking (most important first):\n');
    fprintf('%-6s %-8s %s\n', 'Rank', 'Feature', 'Score');
    for k = 1:numel(idx)
        fprintf('%-6d %-8s %.12f\n', k, names{idx(k)}, scores(idx(k)));
    end

    figure('Color', 'w');
    bar(scores(idx));
    set(gca, 'XTickLabel', names(idx), 'XTick', 1:numel(idx));
    xtickangle(45);
    xlabel('Predictor rank');
    ylabel('Predictor importance score');
    title('MRMR feature importance');
    grid on;
    saveas(gcf, fullfile(resultsDir, 'mrmr_feature_importance.png'));
end

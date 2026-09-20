function run_pipeline()
%RUN_PIPELINE  Reproduce the full bachelor-thesis experiment in MATLAB.

    clc;
    thisDir = fileparts(mfilename('fullpath'));
    addpath(thisDir);

    fprintf('=== 1/5  Edit and encode dataset ===\n');
    edit_dataset();

    fprintf('\n=== 2/5  Normalize to [-1, 1] ===\n');
    normalize();

    fprintf('\n=== 3/5  MRMR feature selection ===\n');
    feature_selection();

    fprintf('\n=== 4/5  90/10 train-test split ===\n');
    split_data();

    fprintf('\n=== 5/5  Train MLP classifier ===\n');
    fprintf('\n-- All 9 features --\n');
    mlp_classifier();

    fprintf('\n-- After dropping eTIV (7) and ASF (9) --\n');
    mlp_classifier('DropFeatures', [7, 9]);
end

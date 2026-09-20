function edit_dataset()
%EDIT_DATASET  Encode the OASIS clinical table and drop Converted cases.
%
% Output columns:
%   1 Group  (+1 Demented, -1 Nondemented)
%   2 Sex    (+1 Male,     -1 Female)
%   3 Age
%   4 EDUC
%   5 SES    (missing values filled with 0, matching the original thesis)
%   6 MMSE   (missing values filled with 4, the observed minimum)
%   7 CDR
%   8 eTIV
%   9 nWBV
%  10 ASF

    [rawPath, outPath] = local_paths();
    T = readtable(rawPath, 'VariableNamingRule', 'preserve');

    keep = ~strcmpi(strtrim(string(T.Group)), 'Converted');
    T = T(keep, :);

    group = nan(height(T), 1);
    group(strcmpi(strtrim(string(T.Group)), 'Demented')) = 1;
    group(strcmpi(strtrim(string(T.Group)), 'Nondemented')) = -1;
    if any(isnan(group))
        error('Unexpected Group labels remain after dropping Converted.');
    end

    sex = nan(height(T), 1);
    sexCol = T.('M/F');
    sex(strcmpi(strtrim(string(sexCol)), 'M')) = 1;
    sex(strcmpi(strtrim(string(sexCol)), 'F')) = -1;
    if any(isnan(sex))
        error('Unexpected sex labels in column M/F.');
    end

    ses = to_numeric(T.SES);
    ses(isnan(ses)) = 0;

    mmse = to_numeric(T.MMSE);
    mmse(isnan(mmse)) = 4;

    data = [group, sex, to_numeric(T.Age), to_numeric(T.EDUC), ses, mmse, ...
            to_numeric(T.CDR), to_numeric(T.eTIV), to_numeric(T.nWBV), ...
            to_numeric(T.ASF)];

    writematrix(data, outPath);
    fprintf('Wrote %d rows to %s\n', size(data, 1), outPath);
end

function values = to_numeric(column)
    if isnumeric(column)
        values = double(column);
    else
        values = str2double(string(column));
    end
end

function [rawPath, outPath] = local_paths()
    root = fileparts(fileparts(mfilename('fullpath')));
    rawPath = fullfile(root, 'data', 'raw', 'oasis_clinical.csv');
    outDir = fullfile(root, 'data', 'processed');
    if ~exist(outDir, 'dir')
        mkdir(outDir);
    end
    outPath = fullfile(outDir, 'dataset2_edited.csv');
end

clc;

X = readmatrix('dataset3_normalized.csv','Range','A1:J336');

[train, test] = dividerand(length(X), 0.9, 0.1);

dataset_train = X(train, :);
dataset_test = X(test, :);

csvwrite('dataset4_train.csv',dataset_train);
csvwrite('dataset5_test.csv',dataset_test);



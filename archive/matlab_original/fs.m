clc;
input = readmatrix('dataset3_normalized.csv','Range','B1:J336');
output = readmatrix('dataset3_normalized.csv','Range','A1:A336');

[idx,scores] = fscmrmr(input,output);
%[idx,scores] = sequentialfs(input,output);
bar(scores(idx))
xlabel('Predictor rank')
ylabel('Predictor importance score')
scores(idx)

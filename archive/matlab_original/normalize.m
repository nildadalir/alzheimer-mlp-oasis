clc;
input = csvread('dataset2_edited.csv');
lb=-1;
ub=1;
Min = min(input);
Max = max(input);

for i = 1:numel(Min)
    input(:,i) = (input(:,i)-Min(i))/(Max(i)-Min(i));
end
input=(ub-lb)*input+lb;
csvwrite('dataset3_normalized.csv',input);
 

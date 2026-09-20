clc;
clear all;
format long;
disp('MLP:');

%--------------------------------- MLP, Train

train_x = readmatrix('dataset4_train.csv','Range','B1:J263');
train_y = readmatrix('dataset4_train.csv','Range','A1:A263');

train_x=train_x';
train_y=train_y';

disp('Reading  was done...');

tic
net=newff(train_x,train_y,[8,4]);
net=train(net,train_x,train_y);
toc

disp('Training was done...');

%--------------------------------- MLP, Test

test_x = readmatrix('dataset5_test.csv','Range','B1:J29');
test_y = readmatrix('dataset5_test.csv','Range','A1:A29');

test_x=test_x';
test_y=test_y';

tic
ODT=sim(net,test_x);

for i=1:length(ODT)
      if ODT(i)>=0
          ODT(i)=1;
      else
          ODT(i)=-1;
      end
end
toc
disp('Testing was done...');

%------------------- Evaluations
TP=0;
TN=0;
FP=0;
FN=0;
for i=1:length(ODT)
    if ODT(i)>=0 && test_y(i)==1
       TP=TP+1; 
    end
    if ODT(i)<0 && test_y(i)==-1
       TN=TN+1; 
    end
    if ODT(i)<0 && test_y(i)==1
       FP=FP+1; 
    end
    if ODT(i)>=0 && test_y(i)==-1
       FN=FN+1; 
    end
end

accuracy=(TP+TN)/(TP+TN+FP+FN);
precision=TP/(TP+FP);
recall=TP/(TP+FN);
f1=2*(precision*recall)/(precision+recall);

text=sprintf('TP=%d',TP); disp(text);
text=sprintf('TN=%d',TN); disp(text);
text=sprintf('FP=%d',FP); disp(text);
text=sprintf('FN=%d',FN); disp(text);

text=sprintf('accuracy=%f',accuracy);   disp(text);
text=sprintf('precision=%f',precision); disp(text);
text=sprintf('recall=%f',recall);       disp(text);
text=sprintf('f1=%f',f1);               disp(text);



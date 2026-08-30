f = fopen('t.txt', 'w');
fprintf(f, 'hi %d\n', 5);
fclose(f);
fprintf('[%s]\n', strtrim(fileread('t.txt')));
x = 42;
save('d.mat', 'x');
clear x
load('d.mat');
fprintf('%d\n', x);
delete('t.txt');
fprintf('%d\n', exist('t.txt', 'file'));

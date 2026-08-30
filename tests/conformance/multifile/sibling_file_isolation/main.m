%% xfail: a sibling .m file with a static error aborts this script, and the error names no file
M = [1 2; 3 4];
fprintf('%d %d\n', size(M, 1), size(M, 2));

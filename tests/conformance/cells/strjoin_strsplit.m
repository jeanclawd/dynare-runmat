%% xfail: strjoin() cannot consume a cell array of strings
p = strsplit('a,b,c', ',');
fprintf('%s\n', strjoin(p, '-'));

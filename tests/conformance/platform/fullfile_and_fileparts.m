p = fullfile('a', 'b', 'c.txt');
[~, n, e] = fileparts(p);
fprintf('%s%s\n', n, e);

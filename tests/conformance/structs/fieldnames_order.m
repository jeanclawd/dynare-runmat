s = struct('b', 1, 'a', 2);
f = fieldnames(s);
fprintf('%s\n', f{1}, f{2});

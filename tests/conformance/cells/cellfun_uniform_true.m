c = {1, 2, 3};
v = cellfun(@(x) x * 2, c);
fprintf('%d\n', sum(v));

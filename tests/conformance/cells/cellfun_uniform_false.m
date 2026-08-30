c = {1, 2, 3};
d = cellfun(@(x) x * 2, c, 'UniformOutput', false);
fprintf('%d\n', d{3});

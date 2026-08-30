c = {};
c{end+1} = 'x';
c{end+1} = 'y';
fprintf('%d %s\n', numel(c), c{2});

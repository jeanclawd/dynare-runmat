s = struct('a', 1, 'b', 2);
s = rmfield(s, 'a');
fprintf('%d %d\n', isfield(s, 'a'), isfield(s, 'b'));

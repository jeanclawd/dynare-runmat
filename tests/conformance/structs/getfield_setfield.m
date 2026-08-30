s = struct('a', 1);
s = setfield(s, 'a', 5);
fprintf('%d\n', getfield(s, 'a'));

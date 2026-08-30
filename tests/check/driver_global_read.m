global M_
M_ = struct('foo', 42);
fprintf('%d\n', read_global());

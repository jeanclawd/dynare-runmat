%% xfail-check: feval(fs{i}, ...) is refused at check AND at run time — a brace index is treated as a comma-list expansion even with a scalar index
%% runs: 7
function y = call(fs, i, a, b)
y = feval(fs{i}, a, b);
end

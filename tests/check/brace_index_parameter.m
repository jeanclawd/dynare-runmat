%% xfail-check: brace indexing a parameter is refused because RunMat cannot prove it is a cell
%% runs: 20
function y = pick(c, i)
y = c{i};
end

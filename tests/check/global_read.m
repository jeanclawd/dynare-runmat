%% xfail-check: the definite-assignment analysis does not treat `global` as bringing the name into scope
%% runs: 42
function y = read_global()
global M_
y = M_.foo;
end

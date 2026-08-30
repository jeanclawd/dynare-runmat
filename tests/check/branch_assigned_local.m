%% xfail-check: definite assignment rejects a local assigned in one branch and read after
%% runs: 1
function y = g(x)
if x > 0
    y = 1;
end
y = y + 0;
end

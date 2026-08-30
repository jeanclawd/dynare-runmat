%% xfail-check: stack overflow — a parameter reassigned in a nested if, then used as an index, crashes check AND run
%% runs: 7
function y = f(a, v)
if a < 1
    if a == 0
        a = a + 1;
    end
    y = v(a);
end
end

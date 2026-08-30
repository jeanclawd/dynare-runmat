o = struct('n', 4);
fprintf('%d\n', bump(o));
function y = bump(o)
y = o.n + 1;
end

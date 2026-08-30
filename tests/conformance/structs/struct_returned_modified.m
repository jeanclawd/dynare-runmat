o = struct('n', 1);
o = setn(o, 8);
fprintf('%d\n', o.n);
function o = setn(o, v)
o.n = v;
end

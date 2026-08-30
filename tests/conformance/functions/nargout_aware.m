[a, b] = f();
fprintf('%d %d\n', a, b);
function [x, y] = f()
x = nargout;
y = 99;
end

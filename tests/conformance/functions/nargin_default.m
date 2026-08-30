fprintf('%d\n', f(1));
function y = f(a, b)
if nargin < 2
b = 10;
end
y = a + b;
end

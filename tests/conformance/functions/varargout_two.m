[a, b] = f();
fprintf('%d %d\n', a, b);
function varargout = f()
varargout{1} = 1;
varargout{2} = 2;
end

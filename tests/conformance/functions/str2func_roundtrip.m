%% xfail: str2func() does not evaluate an anonymous-function source string
h = str2func('@(x) x * 3');
fprintf('%d\n', h(4));

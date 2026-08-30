%% xfail: switch on a char value coerces the operand to f64 and errors
x = 'c';
switch x
case {'b', 'c'}
fprintf('BC\n');
otherwise
fprintf('O\n');
end

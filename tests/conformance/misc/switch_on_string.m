%% xfail: switch on a char value coerces the operand to f64 and errors
x = 'b';
switch x
case 'a'
fprintf('A\n');
case 'b'
fprintf('B\n');
otherwise
fprintf('O\n');
end

%% xfail: eval() does not create the variable in the caller's scope
eval('w = 6;');
fprintf('%d\n', w);

%% xfail: struct array built by indexed auto-vivification
s(1).a = 1;
s(2).a = 2;
fprintf('%d %d\n', numel(s), s(2).a);

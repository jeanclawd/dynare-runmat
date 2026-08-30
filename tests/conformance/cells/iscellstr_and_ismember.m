%% xfail: ismember() rejects char/cellstr inputs, accepting only numeric or logical
c = {'aa', 'bb'};
fprintf('%d %d\n', iscellstr(c), ismember('bb', c));

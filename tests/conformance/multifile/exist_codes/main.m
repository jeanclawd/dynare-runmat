%% xfail: exist() returns 3 (MEX-file) for a plain file where MATLAB returns 2
f = fopen('data.txt', 'w');
fprintf(f, 'x\n');
fclose(f);
mkdir('sub');
q = 1;
fprintf('%d %d %d %d\n', exist('data.txt', 'file'), exist('sub', 'dir'), ...
        exist('q', 'var'), exist('nope.txt', 'file'));

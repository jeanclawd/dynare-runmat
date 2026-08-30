rng(42);
a = rand();
rng(42);
b = rand();
rng(1);
c = randn();
rng(1);
d = randn();
fprintf('%d %d\n', a == b, c == d);

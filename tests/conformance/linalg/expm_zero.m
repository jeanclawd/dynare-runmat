%% xfail: expm() is not implemented in RunMat 0.6.2
E = expm(zeros(2));
fprintf('%d\n', norm(E - eye(2)) < 1e-12);

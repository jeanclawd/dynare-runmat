c();
c();
fprintf('%d\n', c());
function n = c()
persistent k
if isempty(k)
k = 0;
end
k = k + 1;
n = k;
end

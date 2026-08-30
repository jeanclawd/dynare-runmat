global G
G = 7;
bump();
fprintf('%d\n', G);
function bump()
global G
G = G + 1;
end

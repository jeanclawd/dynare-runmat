try
error('My:id', 'text %d', 5);
catch e
fprintf('%s|%s\n', e.identifier, e.message);
end

try
error('boom');
catch e
fprintf('%s\n', e.message);
end

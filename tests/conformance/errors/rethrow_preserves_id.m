try
try
error('X:y', 'inner');
catch e1
rethrow(e1);
end
catch e2
fprintf('%s\n', e2.identifier);
end

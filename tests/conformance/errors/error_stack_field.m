%% xfail: exception object exposing a stack field
try
error('Q:r', 'z');
catch e
fprintf('%d\n', isfield(e, 'stack') || isprop(e, 'stack'));
end

%% xfail: MException object construction/throw
try
throw(MException('A:b', 'msg'));
catch e
fprintf('%s\n', e.identifier);
end

classdef Box
    properties
        v
    end
    methods
        function obj = Box(v)
            obj.v = v;
        end
        function y = getv(obj)
            y = obj.v;
        end
    end
end

classdef Counter < handle
    properties
        n
    end
    methods
        function obj = Counter(start)
            obj.n = start;
        end
        function bump(obj)
            obj.n = obj.n + 1;
        end
    end
end

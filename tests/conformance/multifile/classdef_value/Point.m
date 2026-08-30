classdef Point
    properties
        x
    end
    methods
        function obj = Point(x)
            obj.x = x;
        end
        function obj = setx(obj, v)
            obj.x = v;
        end
    end
end

function interval_index = find_interval(interval,value)
% Find the interval index of value inside interval
    if value > interval(1) && value <= interval(end)
        interval_index = find(value <= interval, 1) - 1;
    elseif value == interval(1)
        interval_index = 1;
    else
        interval_index = nan;
    end
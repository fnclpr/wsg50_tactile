function [ userData ] = data_to_gui( inputs, inputs_raw, targets, time_input, time_target, userData, b_delete_samples )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

    if nargin < 7
        b_delete_samples = true;
    end


    if(isempty(inputs_raw))
        inputs_raw = nan(size(inputs));
    end


    userData = genUserData_(userData, b_delete_samples);
    
    userData.input_cell{1} = inputs;
    userData.input_raw_cell{1} = inputs_raw;
    userData.target_cell{1} = targets;
    userData.time_input_cell{1} = time_input;
    userData.time_target_cell{1} = time_target;
    
    [ userData ] = clearData( userData );


end


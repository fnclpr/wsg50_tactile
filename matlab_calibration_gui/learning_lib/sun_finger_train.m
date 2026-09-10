function [finger_train] = sun_finger_train(finger_train, b_plot_result)
%SUN_TRAIN train various FFNN for the SUN FINGERS

%% inputs
if nargin < 2
    b_plot_result = true;
end

%% Update the train struct
finger_train = struct_finger_train(finger_train);

%% Decimation of train data
finger_train.project_data_decimated_file = sun_finger_decim_db(finger_train.project_data_file, finger_train.finger_decimation_opt);

%% Build train set
if isfield(finger_train,'raw_zero_file')
    [ inputs,targets,~,~ ] = sun_finger_exstract_set( ...
                                finger_train.project_data_decimated_file, ...
                                finger_train.perc_zeros, ...
                                finger_train.b_raw_voltage, ...
                                finger_train.raw_zero_file);
else
    [ inputs,targets,~,~ ] = sun_finger_exstract_set( ...
                                finger_train.project_data_decimated_file, ...
                                finger_train.perc_zeros, ...
                                finger_train.b_raw_voltage);
end

%% TRAIN     
finger_train.pca_train_out = sun_pca_train_net(finger_train.pca_train_opt, inputs, targets);
        
if b_plot_result
    sun_finger_test_net(finger_train);
end

end


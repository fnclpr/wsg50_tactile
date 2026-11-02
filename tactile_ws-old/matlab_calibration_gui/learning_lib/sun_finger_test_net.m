function [performance, outputs] = sun_finger_test_net(finger_train, project_data_file, perc_zeros)
%SUN_FINGERS_TEST_NET test the trained ANN
%   if no test file provided, use sun_train_opt.test_file

%% Input

if ischar(finger_train)
    loaded_file = load(finger_train);
    finger_train = loaded_file.finger_train;
    clear loaded_file
end

if nargin < 2 || isempty(project_data_file)
    project_data_file = finger_train.project_data_file;
end

if nargin < 3
    perc_zeros = finger_train.perc_zeros;
end

%% Build train set
if isfield(finger_train,'raw_zero_file')
    [ inputs, targets, time_inputs, time_targets ] = sun_finger_exstract_set( ...
                                project_data_file, ...
                                perc_zeros, ...
                                finger_train.b_raw_voltage, ...
                                finger_train.raw_zero_file);
else
    [ inputs, targets, time_inputs, time_targets ] = sun_finger_exstract_set( ...
                                project_data_file, ...
                                perc_zeros, ...
                                finger_train.b_raw_voltage);
end

%% Test net
[performance, outputs] = sun_pca_test_net( finger_train.pca_train_out, inputs, targets);

if nargout == 0
    err_v=finger_train_plot_compare(time_targets,targets',outputs, true)
end

end


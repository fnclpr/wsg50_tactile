clear all, close all force

%% Add path for lib
path_to_repo = [userpath '/matlab_calibration_gui/']; % <= mod this!
addpath([ path_to_repo 'gui_lib']);
addpath([ path_to_repo 'learning_lib']);
addpath([ path_to_repo 'learning_lib/train_lib']);
train_lib_load_path();

%% Initstruct

% Run opt
output_file_prefix = ['F004_test_train_out_'];
input_file = 'F004_test';
raw_zero_file = ''; %<-- needed if raw_voltage=true

%% Build models

finger_train = struct_finger_train();
    
% finger_train
%     project_data_file : string
%     project_data_decimated_file : string
%     finger_decimation_opt : finger_decimation_opt
%         b_raw_voltage : bool
%         min_wrench : double vector
%         max_wrench : double vector
%         decimation_radius : double vector
%     perc_zeros : double
%     b_raw_voltage : bool
%     raw_zero_file : string
%     broken_cells : int vector %from projectData
%     finger_id : string %from projectData
%     pca_train_opt : sun_pca_train_opt
%         checkpoint_file : string
%         b_use_gpu : bool
%         pca : int
%         net : matlab_network_struct
%     pca_train_out : sun_pca_train_out
%         checkpoint_file : string
%         b_use_gpu : bool
%         pca : int
%         net : matlab_network_struct

% files
finger_train.project_data_file = input_file;

% change mode
%finger_train.b_raw_voltage = true; finger_train.raw_zero_file = raw_zero_file;
finger_train.finger_decimation_opt = struct_finger_decimation_opt();
finger_train.finger_decimation_opt.b_raw_voltage = false;
finger_train.finger_decimation_opt.decimation_radius = 0.2;
finger_train.finger_decimation_opt.input_scale = 'minmax';
finger_train.decimation_opt.target_scale = 'minmax';
%finger_train.pca_train_opt.pca = 15;
pca_train_opt.net = fitnet(90*ones(1,6));
finger_train.pca_train_opt.b_use_gpu = true;
finger_train.pca_train_opt.net.divideParam.trainRatio = 50/100;
finger_train.pca_train_opt.net.divideParam.valRatio = 40/100;
finger_train.pca_train_opt.net.divideParam.testRatio = 10/100;
finger_train.pca_train_opt.net.divideFcn = 'dividerand';
finger_train.pca_train_opt.net.trainFcn = 'trainscg';
finger_train.pca_train_opt.net.trainParam.epochs = 100000;
finger_train.pca_train_opt.net.trainParam.max_fail = 150;

%% TRAIN
%uncomment the following line to retrain
%finger_train.train_opt.net = finger_train.train_out.net;
finger_train = sun_finger_train(finger_train);

%% SAVE
output_file = [ output_file_prefix datestr(now,'yyyy_mm_dd__HH_MM')];
save(output_file, 'finger_train')

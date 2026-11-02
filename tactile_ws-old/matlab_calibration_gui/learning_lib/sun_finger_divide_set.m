function [userData1, userData2] = sun_finger_divide_set(input_file , file2_perc)
%
%

%% LOAD LIB
[filepath,name,ext] = fileparts(mfilename('fullpath'));
addpath(filepath);
addpath([filepath '/../gui_lib']);

%% Load Input
disp(['sun_finger_divide_set - loading...']);
loaded_file = load(input_file);
[inputs,input_raw,targets,time_inputs,time_targets ] = mergeData(loaded_file.userData,false);
disp(['sun_finger_divide_set - loading DONE']);

%% dividerand
disp(['sun_finger_divide_set - dividerand...']);
[trainInd,valInd,test] = dividerand(size(inputs,2),1-file2_perc,file2_perc,0);

%% userData1
inputs_1=inputs(:,trainInd);
input_raw_1=input_raw(:,trainInd);
targets_1=targets(:,trainInd);
time_inputs_1=time_inputs(trainInd);
time_targets_1=time_targets(trainInd);

userData1 = data_to_gui( inputs_1, input_raw_1, targets_1, time_inputs_1, time_targets_1, loaded_file.userData );

%% userData2
inputs_2=inputs(:,valInd);
input_raw_2=input_raw(:,valInd);
targets_2=targets(:,valInd);
time_inputs_2=time_inputs(valInd);
time_targets_2=time_targets(valInd);

userData2 = data_to_gui( inputs_2, input_raw_2, targets_2, time_inputs_2, time_targets_2, loaded_file.userData );


end


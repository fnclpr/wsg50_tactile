function decimated_file = sun_finger_decim_db(data_file, finger_decimation_opt)
%SUN_TRAIN_DECIM Summary of this function goes here
%   Detailed explanation goes here

%% check tmp folder
db_folder = 'db_decim';
if ~exist(db_folder,'dir')
    mkdir(db_folder);
end

%% Case radius is zero
if all(finger_decimation_opt.decimation_radius == 0)
    disp('sun_finger_decim_db - all radii are ZERO!')
    decimated_file = data_file;
    return
end

%% Build Tmp file name

[filepath,filename,fileext] = fileparts(data_file);

decimated_file = [ db_folder ...
    '/' filename '_decim_R_'...
    regexprep(num2str(round(finger_decimation_opt.decimation_radius*1000)),'\s+','_') ...
    '_IS_' num2str(finger_decimation_opt.input_scale) '_TS_' num2str(finger_decimation_opt.target_scale)
     ];
if finger_decimation_opt.b_raw_voltage && all(finger_decimation_opt.input_scale ~= 0)
    decimated_file = [decimated_file '_raw'];
end

%% Check file exist

if (exist(decimated_file,'file') || exist([decimated_file '.mat'],'file'))
    disp('sun_finger_decim_db - using tmp file!')
    return
end

%% decim

projectData = sun_finger_decim(data_file, finger_decimation_opt);
disp('sun_finger_decim_db - save tmp file')
t0 = tic;
save(decimated_file , 'projectData');
disp('sun_finger_decim_db - save tmp file DONE')
toc(t0);

end


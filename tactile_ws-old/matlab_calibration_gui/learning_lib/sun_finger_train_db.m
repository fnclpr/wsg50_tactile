function [finger_train] = sun_finger_train_db(finger_train, b_plot_result, trained_file)
%SUN_TRAIN train various FFNN for the SUN FINGERS

%% inputs
if nargin < 2
    b_plot_result = true;
end

if nargin < 3
    trained_file = [];
end

%% check tmp folder
% db_folder = 'db_train';
% if ~exist(db_folder,'dir')
%     mkdir(db_folder);
% end

%% Build Tmp file name

%trained_file = trained_file;

%% Check file exist

if (exist(trained_file,'file') || exist([trained_file '.mat'],'file'))
    disp('sun_finger_train_db - using tmp file!')
    loaded_file = load(trained_file);
    finger_train = loaded_file.finger_train;
    return
end

%% TRAIN

finger_train = sun_finger_train(finger_train, b_plot_result);

%% SAVE

if ~isempty(trained_file)
    disp('sun_finger_train_db - save tmp file')
    t0 = tic;
    save(trained_file , 'finger_train');
    disp('sun_finger_train_db - save tmp file DONE')
    toc(t0);
end

end


clear all, close all force

%% Add path for lib
path_to_repo = '../'; % <= mod this!
addpath([ path_to_repo 'learning_lib']);

%% Initstruct

% Run opt
tmp_train_folder_name = 'F003_19_10_9';
output_file_prefix = ['F003_resina_train_out_'];
input_file = 'F003_resina_calib_exp_2019_10_03__16_05_Z1';
raw_zero_file = 'F003_raw_ZERO';

% common train opt
train_perc_zeros = 0.6/100;

% cross_valid opt
cross_valid_perc = 30/100;
cross_valid_decim_b_raw_voltage = true;
cross_valid_decim_radius = [0.05 0.08 0.1];
cross_valid_perc_zeros = train_perc_zeros;

%% Train Combinations

raw_voltage_cell = {
    false
    true
    };
decimation_radius_cell = {
    0.5
    0.2
    0.1
    0.0
    };
decimation_mode_cell = {
    {'minmax', 'minmax'}
    {0, 'minmax'}
    };
pca_cell = {
    0
    15
    10
    };
net_size_cell = {
    %90*ones(1,6)
    50*ones(1,6)
    25*ones(1,6) 
    [25 15 10] 
    [10 10]
    };
num_net_to_create = 2;

%% Build models

finger_cross_train = get_finger_cross_train_struct();

% finger_cross_train
%     input_file : string
%     cross_valid_perc : double
%     train_file : string
%     cross_valid_file : string
%     decimated_cross_valid_file : string
%     cross_valid_decimation_opt : finger_decimation_opt
%     cross_valid_perc_zeros : double
%     finger_trains{} : cell of finger_train
%     
% finger_train
%     data_file : string
%     decimated_file : string
%     decimation_opt : finger_decimation_opt
%     perc_zeros : double
%     b_raw_voltage : bool
%     raw_zero_file : string
%     remove_volts : int vector %from userData
%     finger_id : string %from userData
%     train_opt : sun_pca_train_opt
%     train_out : sun_pca_train_out

finger_cross_train.input_file = input_file;
finger_cross_train.cross_valid_perc = cross_valid_perc;
finger_cross_train.cross_valid_decimation_opt.b_raw_voltage = cross_valid_decim_b_raw_voltage;
finger_cross_train.cross_valid_decimation_opt.decimation_radius = cross_valid_decim_radius;
finger_cross_train.cross_valid_perc_zeros = cross_valid_perc_zeros;

disp('Build train options...')
iii = 0;
for i1=1:numel(raw_voltage_cell)
    for i2=1:numel(decimation_radius_cell)
        for i3=1:numel(decimation_mode_cell)
            for i4=1:numel(pca_cell)
                for i5=1:numel(net_size_cell)
                    for i6=1:num_net_to_create

                        iii = iii+1;
                        disp(['Build train options ' num2str(iii)]);

                        %finger_train = get_finger_train_struct();

                        %raw_voltage_cell i1
                        finger_train.decimation_opt.b_raw_voltage = raw_voltage_cell{i1};
                        finger_train.b_raw_voltage = raw_voltage_cell{i1};

                        %decimation_radius_cell i2
                        finger_train.decimation_opt.decimation_radius = decimation_radius_cell{i2};
                        
                        %decimation_mode_cell i3
                        finger_train.decimation_opt.input_scale = decimation_mode_cell{i3}{1};
                        finger_train.decimation_opt.target_scale = decimation_mode_cell{i3}{2};

                        %pca_cell i4
                        finger_train.train_opt.pca = pca_cell{i4};

                        %net_size_cell i5
                        finger_train.train_opt.net = fitnet(net_size_cell{i5});
                        finger_train.train_opt.net.divideParam.trainRatio = 50/100;
                        finger_train.train_opt.net.divideParam.valRatio = 40/100;
                        finger_train.train_opt.net.divideParam.testRatio = 10/100;
                        finger_train.train_opt.net.divideFcn = 'dividerand';
                        finger_train.train_opt.net.trainFcn = 'trainscg';
                        finger_train.train_opt.net.trainParam.epochs = 100;%100000;
                        finger_train.train_opt.net.trainParam.max_fail = 150;

                        %varie
                        finger_train.perc_zeros = train_perc_zeros;
                        finger_train.raw_zero_file = raw_zero_file;

                        %add in cell
                        finger_cross_train.finger_trains{end+1} = finger_train;
                    end
                end
            end
        end
    end
end

disp(['I will train ' num2str(numel(finger_cross_train.finger_trains)) ' NN!'])
%disp('press a key...')
%pause
disp('=========START!=============')

%% TRAIN
[finger_train_best, finger_cross_train, index_best] = sun_finger_cross_train(finger_cross_train, tmp_train_folder_name);
finger_train = finger_train_best;

%% SAVE
output_file = [ output_file_prefix datestr(now,'yyyy_mm_dd__HH_MM')];
save(output_file, 'finger_train')

function [finger_train_best, finger_cross_train, index_best] = sun_finger_cross_train(finger_cross_train, folder_name)
%SUN_TRAIN train various FFNN using tmp files
%   sun_train_opt can be a vector

%% Input
if nargin < 2 
    folder_name = 'default';
end

%% check tmp folder
db_folder = 'db_train';
if ~exist(db_folder,'dir')
    mkdir(db_folder);
end

if ~exist([db_folder '/' folder_name],'dir')
    mkdir([db_folder '/' folder_name]);
end

%% Build tmp file prefix

tmp_file_name_prefix = [ db_folder '/' folder_name '/' '_tmp_trained_' ];

%% DIVIDE TRAIN AND CROSS VALID SET

[   finger_cross_train.train_file, ...
    finger_cross_train.cross_valid_file] ...
        = ...
            sun_finger_divide_set_db( ...
                finger_cross_train.input_file, ...
               	finger_cross_train.cross_valid_perc, ...
             	['_CROSS_TRAIN_SET_' folder_name], ...
             	['_CROSS_VALID_SET_' folder_name], ...
                folder_name );
            
%% DECIM CROSS VALID SET

finger_cross_train.decimated_cross_valid_file = ...
    sun_finger_decim_db( ...
        finger_cross_train.cross_valid_file, ...
        finger_cross_train.cross_valid_decimation_opt);
    
%% Update the train cell

num_trains = numel(finger_cross_train.finger_trains);
finger_cross_train.finger_trains{1}.data_file = finger_cross_train.train_file;
finger_cross_train.finger_trains{1} = get_finger_train_struct(finger_cross_train.finger_trains{1});
for i=2:num_trains
    
    finger_cross_train.finger_trains{i}.data_file = finger_cross_train.train_file;
    finger_cross_train.finger_trains{i}.remove_volts = finger_cross_train.finger_trains{1}.remove_volts;
    finger_cross_train.finger_trains{i}.finger_id = finger_cross_train.finger_trains{1}.finger_id;
    finger_cross_train.finger_trains{i} = get_finger_train_struct(finger_cross_train.finger_trains{i});
    
end

%% TRAIN LOOP

t0 = tic;
disp('sun_finger_cross_train - multiple trains...')
for i=1:num_trains
    
    t_for = tic;
    disp([ 'sun_finger_cross_train - START ' num2str(i) '/' num2str(num_trains) ] )
    
    % Select the finger train struct
    finger_train = finger_cross_train.finger_trains{i};
    
    % TMP file name
    trained_file = [tmp_file_name_prefix 'index_' num2str(i)];
    
    % finger_train catched
    try
        % train
        finger_train = sun_finger_train_db( ...
                        finger_train, false, trained_file);
        % cross validation
        finger_train.train_out.cross_valid_performance = ...
            sun_finger_test_net( ...
                finger_train, ...
                finger_cross_train.decimated_cross_valid_file, ...
                finger_cross_train.cross_valid_perc_zeros);
    catch ME
        switch ME.identifier
            case {'parallel:gpu:array:pmaxsize', 'parallel:gpu:array:OOM' }
                warning('on')
                warning(['The train ' num2str(i) ' failed due to GPU memory fail'])
                finger_train.train_out.train_performance = inf;
                finger_train.train_out.cross_valid_performance = inf;
            otherwise
                rethrow(ME)
        end
    end
    
    % save result in cell
    finger_cross_train.finger_trains{i} = finger_train;
    
    % end display
    disp([ 'sun_finger_cross_train - DONE ' num2str(i) '/' num2str(num_trains) ] )
    disp([ 'sun_finger_cross_train - train_performance =  ' num2str(finger_train.train_out.train_performance) ] )
    disp([ 'sun_finger_cross_train - cross_valid_performance =  ' num2str(finger_train.train_out.cross_valid_performance) ] )
    toc(t_for);
    disp(['sun_finger_cross_train - global elapsed time = ' num2str(toc(t0)) ]);
end
    
disp(['sun_train_multi - TRAIN DONE global elapsed time = ' num2str(toc(t0)) ]);

%% Find the best train

disp(['sun_finger_cross_train - find best net' ]);
    
%find min performance on cross valid
index_best = 1;
for i = 2 : num_trains
    if finger_cross_train.finger_trains{i}.train_out.cross_valid_performance ...
            < finger_cross_train.finger_trains{index_best}.train_out.cross_valid_performance
       index_best = i; 
    end
end

disp(['sun_finger_cross_train - best net is ' num2str(index_best) ]);
    
finger_train_best = finger_cross_train.finger_trains{index_best};
    
%% Final PLOT
sun_finger_test_net(finger_train_best,finger_cross_train.input_file);

end


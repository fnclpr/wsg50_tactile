function [output_file1, output_file2] = sun_finger_divide_set_db(input_file , file2_perc, file1_postfix, file2_postfix, folder_name)
%
%

%% Input
if nargin < 3
    file1_postfix = '_divided_1';
end
if nargin < 4
    file2_postfix = '_divided_2';
end
if nargin < 5
    folder_name = 'default';
end

%% check tmp folder
db_folder = 'db_divide_set';
if ~exist(db_folder,'dir')
    mkdir(db_folder);
end

if ~exist([db_folder '/' folder_name],'dir')
    mkdir([db_folder '/' folder_name]);
end

%% Build Tmp file names
[filepath,filename,fileext] = fileparts(input_file);

output_file1 = [ db_folder '/' folder_name '/' filename file1_postfix ];
output_file2 = [ db_folder '/' folder_name '/' filename file2_postfix ];

%% Check file exist

b_exist_file1 = (exist(output_file1,'file') || exist([output_file1 '.mat'],'file'));
b_exist_file2 = (exist(output_file2,'file') || exist([output_file2 '.mat'],'file'));

if b_exist_file1 && b_exist_file2
    disp('sun_finger_divide_set_db - using tmp file!')
    return
elseif b_exist_file1 || b_exist_file2
    error('only one of output file exsist! delete it to continue!')
end

%% Divide

[userData1, userData2] = sun_finger_divide_set(input_file , file2_perc);

%% Save1
disp('sun_finger_divide_set_db - save...')

userData = userData1;
save(output_file1, 'userData');

%% Save2
userData = userData2;
save(output_file2, 'userData');

disp('sun_finger_divide_set_db - save DONE!')

end


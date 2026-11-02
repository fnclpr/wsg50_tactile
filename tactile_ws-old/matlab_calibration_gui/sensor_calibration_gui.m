function varargout = sensor_calibration_gui(varargin)
% SENSOR_CALIBRATION_GUI MATLAB code for sensor_calibration_gui.fig
%      SENSOR_CALIBRATION_GUI, by itself, creates a new SENSOR_CALIBRATION_GUI or raises the existing
%      singleton*.
%
%      H = SENSOR_CALIBRATION_GUI returns the handle to a new SENSOR_CALIBRATION_GUI or the handle to
%      the existing singleton*.
%<
%      SENSOR_CALIBRATION_GUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in SENSOR_CALIBRATION_GUI.M with the given input arguments.
%
%      SENSOR_CALIBRATION_GUI('Property','Value',...) creates a new SENSOR_CALIBRATION_GUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before sensor_calibration_gui_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to sensor_calibration_gui_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help sensor_calibration_gui

% Last Modified by GUIDE v2.5 04-Jun-2018 16:21:42

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @sensor_calibration_gui_OpeningFcn, ...
                   'gui_OutputFcn',  @sensor_calibration_gui_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

%Update text in the gui
function handles = updateVisualParams(handles)
    handles.textMu.String = num2str(handles.userData.mu_);
    handles.editAlpha.String = num2str(handles.userData.alpha_);
    handles.editGamma.String = num2str(handles.userData.gamma_);
    
    handles.SelectFn.String = central_Fn_vect_2_string(handles.userData.Fn_interval);
    
    handles.info_text.String = [handles.userData.finger_id '| BAD CELLS = ' num2str(handles.userData.remove_volts) ];
    
    
function handles = clearTimers(handles,b_create)
% Destroy timers
if isfield(handles, 'timer') && isvalid(handles.timer) &&  strcmp(get(handles.timer, 'Running'), 'on')
    stop(handles.timer);
    delete(handles.timer)
end
if isfield(handles, 'timer_refresh') && isvalid(handles.timer_refresh) && strcmp(get(handles.timer_refresh, 'Running'), 'on')
    stop(handles.timer_refresh);
    delete(handles.timer_refresh)
end
if isfield(handles, 'timer_plotVolt') && isvalid(handles.timer_plotVolt) && strcmp(get(handles.timer_plotVolt, 'Running'), 'on')
    stop(handles.timer_plotVolt);
    delete(handles.timer_plotVolt)
end
if isfield(handles, 'timer_plotActualPoint') && isvalid(handles.timer_plotActualPoint) && strcmp(get(handles.timer_plotActualPoint, 'Running'), 'on')
    stop(handles.timer_plotActualPoint);
    delete(handles.timer_plotActualPoint)
end

if b_create
    % Create timers
    %main timer
    handles.timer = timer(...
        'Name' , 'main_timer' , ...
        'ExecutionMode', 'fixedRate', ...       % Run timer repeatedly.
        'Period', handles.userData.Ts, ...               % Initial period.
        'TimerFcn', {@update_timer,handles.figure1}); % Specify callback function.

    %timer refresh all...
    handles.timer_refresh = timer(...
        'Name' , 'timer_refresh' , ...
        'ExecutionMode', 'fixedRate', ...       % Run timer repeatedly.
        'Period', 10*handles.userData.Ts, ...               % Initial period.
        'TimerFcn', {@update_timer_refresh,handles.figure1}); % Specify callback function.

    %timer to plot volts
    handles.timer_plotVolt = timer(...
        'Name' , 'timer_plotVolt' , ...
        'ExecutionMode', 'fixedRate', ...       % Run timer repeatedly.
        'Period', 4*handles.userData.Ts, ...               % Initial period.
        'TimerFcn', {@update_timer_plotVolt,handles.figure1}); % Specify callback function.

    %timer to plot actual point
    handles.timer_plotActualPoint = timer(...
        'Name' , 'timer_timer_plotActualPoint' , ...
        'ExecutionMode', 'fixedRate', ...       % Run timer repeatedly.
        'Period', 3*handles.userData.Ts, ...               % Initial period.
        'TimerFcn', {@update_ActualPoint,handles.figure1}); % Specify callback function.
end

function handles = if_convertToGPU(handles)
if(handles.guiData.b_useGPU)
    handles.userData.input_cell = convertMatCell2GPU(handles.userData.input_cell);
    handles.userData.input_raw_cell = convertMatCell2GPU(handles.userData.input_raw_cell);
    handles.userData.target_cell = convertMatCell2GPU(handles.userData.target_cell);
    handles.userData.target_plot_cell = convertMatCell2GPU(handles.userData.target_plot_cell);
    handles.userData.time_target_cell = convertMatCell2GPU(handles.userData.time_target_cell);
    handles.userData.time_input_cell = convertMatCell2GPU(handles.userData.time_input_cell);
    handles.userData.handles.zoneTrasform = convertMatCell2GPU(handles.userData.handles.zoneTrasform);
end

function userData = convertFromGPU(userData)
    userData.input_cell = convertMatCellFromGPU(userData.input_cell);
    userData.input_raw_cell = convertMatCellFromGPU(userData.input_raw_cell);
    userData.target_cell = convertMatCellFromGPU(userData.target_cell);
    userData.target_plot_cell = convertMatCellFromGPU(userData.target_plot_cell);
    userData.time_target_cell = convertMatCellFromGPU(userData.time_target_cell);
    userData.time_input_cell = convertMatCellFromGPU(userData.time_input_cell);

function handles = clearHandles(handles)

%refresh timers
handles = clearTimers(handles,true);

handles.dependentData.central_Fn_vect = calcCentralFn(handles.userData.Fn_interval);

%Update selecter of zones
handles.SelectCentroid.String = {};
for i = 1:handles.userData.num_zones
    handles.SelectCentroid.String{i} = num2str(i);
end

%vars di flusso
handles.started = false;
handles.lastSinglePointPlotted = [nan nan nan];
handles.plotVoltButton = false;
handles.count_to_refresh = handles.guiData.refreshCount;

%vars plot volts
handles.plotVoltValues = zeros(25,150);
handles.plotVoltTime = linspace(0, 5, 150);
handles.plotVData.actualVoltages = zeros(25,1);
handles.plotVData.actualVoltagesTime = 5;

handles = clearRosVars(handles);

handles.zoneTrasform = genZoneTrMatrix( handles.userData.zone_radius_centers , handles.userData.sf_radius, handles.userData.sc_z_sf, handles.userData.angle_center_lines );

handles = updateVisualParams(handles);

handles = if_convertToGPU(handles);

% Update handles structure
guidata(handles.figure1, handles);

refresh_all(handles.figure1, handles);

%start timer_refresh
if strcmp(get(handles.timer_refresh, 'Running'), 'off')
    start(handles.timer_refresh);
end



% --- Executes just before sensor_calibration_gui is made visible.
function sensor_calibration_gui_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to sensor_calibration_gui (see VARARGIN)

% Choose default command line output for sensor_calibration_gui
handles.output = hObject;

[filepath,name,ext] = fileparts(mfilename('fullpath'));
addpath(filepath);
addpath([filepath '/gui_lib']);

% User Vars
%%%%%%to save
handles.userData.finger_id = 'H004_cartone';
%handles.userData.remove_volts = [4 6 10];
handles.userData = genUserData_(handles.userData);
disp('USER DATA')
handles.userData

handles.guiData = genGUIData_();
disp('GUI DATA')
handles.guiData

%Clear handles
handles = clearHandles(handles);

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes sensor_calibration_gui wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = sensor_calibration_gui_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



function [handles] = plotCentroid(centroid, zone, handles)

if ~(isfield(handles.h_CentroidPlot, 'CentroidPoint'))
    hold(handles.plotCentroid,'on')
    handles.h_CentroidPlot.CentroidPoint = plot(handles.plotCentroid, 0, 0,'b*');
    hold(handles.plotCentroid,'off')
end

centroid = visual_rotate(centroid);

handles.h_CentroidPlot.CentroidPoint.XData = centroid(1);
handles.h_CentroidPlot.CentroidPoint.YData = centroid(2);

%Update zone color
for i=1:handles.userData.num_zones
    if(i == zone)       
        set(handles.h_CentroidPlot.h_zone(zone), 'Color' , [0 1 0]);
    else
        set(handles.h_CentroidPlot.h_zone(i), 'Color' , [1 0 0]);
    end
end
%drawnow
    


function handles = calculateOffsetVoltages(handles)

sub = handles.ros.subCalib;

off = zeros(25,1);
n_mean = 50;
for i=1:n_mean
   calib_msg = sub.receive;
   off = off + calib_msg.Data(handles.ros.voltIndex);
   pause(2*handles.userData.Ts);
end
handles.offsetVoltages = off/n_mean;

% --- Executes on button press in StartButton.
function StartButton_Callback(hObject, eventdata, handles)
% hObject    handle to StartButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if ~isfield(handles,'offsetVoltages')
   handles.StartButton.Enable = 'off';
   handles.ButtonLoad.Enable = 'off';
   handles = calculateOffsetVoltages(handles);
   
   handles.StartButton.String = 'Start';
   handles.StartButton.BackgroundColor = [0 1 0];
   handles.started = false;
   handles.saveButton.Enable = 'off';
   handles.StartButton.Enable = 'on';
   handles.ButtonLoad.Enable = 'on';

elseif(handles.started)
    
    %stop timer
    if strcmp(get(handles.timer, 'Running'), 'on')
        stop(handles.timer);
    end
    if strcmp(get(handles.timer_plotActualPoint, 'Running'), 'on')
        stop(handles.timer_plotActualPoint);
    end
    

    handles.StartButton.String = 'Start';
    handles.StartButton.BackgroundColor = [0 1 0];
    handles.started = false;
    handles.saveButton.Enable = 'on';
    handles.ButtonLoad.Enable = 'on';
    handles.ButtonCalcOff.Enable = 'on';
    
else
    handles.StartButton.String = 'Stop';
    handles.StartButton.BackgroundColor = [1 0 0];
    handles.started = true;
    handles.saveButton.Enable = 'off';
    handles.ButtonLoad.Enable = 'off';
    handles.ButtonCalcOff.Enable = 'off';
 
    %start timer
    if strcmp(get(handles.timer, 'Running'), 'off')
        start(handles.timer);
    end
    if strcmp(get(handles.timer_plotActualPoint, 'Running'), 'off')
        start(handles.timer_plotActualPoint);
    end
    
end

guidata(hObject, handles);
handles = refresh_all(hObject, handles);
guidata(hObject, handles);


% -- User FCNS --

% Clear plot(Fn)
function handles = drawBasic(handles)

%// radius
r = 1;
%// center
c = [0 0];
pos = [c-r 2*r 2*r];

%PLOT XY
hold(handles.MainPlot,'off')
rectangle(handles.MainPlot,'Position',pos,'Curvature',[1 1])
xlabel(handles.MainPlot,'Fx') , ylabel(handles.MainPlot,'Fy') , grid(handles.MainPlot, 'on');
hold(handles.MainPlot,'on');
handles.h_xy = plot(handles.MainPlot, nan, nan, 'b*');
handles.h_xy.ZData = 1;
axis(handles.MainPlot,'square')

%PLOT XM
hold(handles.plot_xm,'off')
rectangle(handles.plot_xm,'Position',pos,'Curvature',[1 1])
xlabel(handles.plot_xm,'Fx') , ylabel(handles.plot_xm,'Mz') , grid(handles.plot_xm, 'on');
hold(handles.plot_xm,'on');
handles.h_xm = plot(handles.plot_xm, nan, nan, 'b*');
handles.h_xm.ZData = 1;
axis(handles.plot_xm,'square')

%PLOT YM
hold(handles.plot_ym,'off')
rectangle(handles.plot_ym,'Position',pos,'Curvature',[1 1])
xlabel(handles.plot_ym,'Mz') , ylabel(handles.plot_ym,'Fy') , grid(handles.plot_ym, 'on');
hold(handles.plot_ym,'on');
handles.h_ym = plot(handles.plot_ym, nan, nan, 'b*');
handles.h_ym.ZData = 1;
axis(handles.plot_ym, 'square')

% Plot3d -----
    hold(handles.plot3d,'off')
    [xs,ys,zs] = sphere(100);
    hs = surf(handles.plot3d,xs,ys,zs);
    shading(handles.plot3d, 'interp')
    colormap(handles.plot3d , 'summer')
    if ~isvalid(hs)
       refresh_all(handles.figure1, handles);
       return
    end
    alpha(hs,0.2);
    xlabel(handles.plot3d, 'Fx') , ylabel(handles.plot3d, 'Fy'), zlabel(handles.plot3d, 'Mz') , grid( handles.plot3d, 'on');
    axis( handles.plot3d, 'square')


%Plot base of plotCentroid
if ~(isfield(handles,'h_CentroidPlot'))
    handles.h_CentroidPlot = struct;
end
if  ~(isfield(handles.h_CentroidPlot,'CentroidPoint')) %singleton
    axes(handles.plotCentroid);
    hold(handles.plotCentroid,'off')
    rectangle('Position',pos)
    xlabel('x') , ylabel('y') , grid on;
    
    %plot circles
    c = [0 0];
    for i = 1:length(handles.userData.zone_radius_intervals)
        r = handles.userData.zone_radius_intervals(i);
        pos = [c-r 2*r 2*r];
        rectangle('Position',pos,'Curvature',[1 1])
        hold on
    end
    
    %Plot Lines
    rho = [handles.userData.zone_radius_intervals(1) 1];
    for angle = handles.userData.angle_bound_lines 
        plotLineHo(handles.plotCentroid,rho,angle);
    end

    %Plot numbers
    i = 1;
    %rr = 0.7;
    handles.h_CentroidPlot.h_zone(i) = plot(0,0,'rs','MarkerSize',30,'LineWidth',5);
    text(0,0,num2str(i),'FontSize',20,'HorizontalAlignment','center')
    for radii = handles.userData.zone_radius_centers
        for angle = handles.userData.angle_center_lines
            i = i+1;
            [x,y] = pol2cart(angle,radii);
            xy = visual_rotate([x;y]);
            x = xy(1); y = xy(2);
            handles.h_CentroidPlot.h_zone(i) = plot(x,y,'rs','MarkerSize',30,'LineWidth',5);
            text(x,y,num2str(i),'FontSize',20,'HorizontalAlignment','center')
        end
    end
    handles.h_CentroidPlot.CentroidPoint = plot(handles.plotCentroid, 0, 0,'b*');
    hold off
    %axis([-1 1 -1 1])
    axis([-0.006 0.006 -0.006 0.006])
    axis square
end

function plotLineHo(ax,rho,ang)
polar(ax,ang*ones(1,length(rho)),rho,'k')

% Update all
function handles = refresh_all(hObject, handles)

handles.count_to_refresh = handles.guiData.refreshCount;

%clear all axs
 cla(handles.MainPlot)
 cla(handles.plot_xm)
 cla(handles.plot_ym)
 cla(handles.plot3d)
 %cla(handles.plotCentroid)

%draw basic figures
handles = drawBasic(handles);
guidata(hObject, handles);

%what i should plot?
indexSelFn = handles.SelectFn.Value;
indexSelZone = handles.SelectCentroid.Value;

%select target to plot
target = handles.userData.target_plot_cell{indexSelZone,indexSelFn};

if isempty(target)
    handles.textSavedPoints.String = '0';
    guidata(hObject, handles);
    return
end

%update saved count
handles.textSavedPoints.String = num2str(size(target,2));

%what plot?
if handles.sliderRadius.Value > 1
    plotIndex = 1:size(target,2);
else
    plotIndex = sqrt( sum(target.^2)  ) < handles.sliderRadius.Value;
end
if( ~any(plotIndex) )
    guidata(hObject, handles);
    return
end

%PLOT!
hold(handles.MainPlot,'on')
plot(handles.MainPlot, target(1,plotIndex), target(2,plotIndex),'r*');
%plot(handles.MainPlot, target(2,plotIndex), -target(1,plotIndex),'r*');
axis(handles.MainPlot,'square')
    
hold(handles.plot_xm,'on')
plot(handles.plot_xm, target(1,plotIndex), target(3,plotIndex),'r*');
%plot(handles.plot_xm, target(2,plotIndex), target(3,plotIndex),'r*');
axis(handles.plot_xm,'square')
    
hold(handles.plot_ym,'on')
plot(handles.plot_ym, target(3,plotIndex) , target(2,plotIndex) ,'r*'); 
%plot(handles.plot_ym, target(3,plotIndex) , -target(1,plotIndex) ,'r*'); 
axis(handles.plot_ym,'square')


hold(handles.plot3d,'on')
plot3(handles.plot3d, target(1,plotIndex), target(2,plotIndex), target(3,plotIndex),'r*'); 
axis(handles.plot3d,'square')







% --- Executes on selection change in SelectFn.
function SelectFn_Callback(hObject, eventdata, handles)
% hObject    handle to SelectFn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns SelectFn contents as cell array
%        contents{get(hObject,'Value')} returns selected item from SelectFn
%stop timer
refresh_all(hObject, handles);




% --- Executes during object creation, after setting all properties.
function SelectFn_CreateFcn(hObject, eventdata, handles)
% hObject    handle to SelectFn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

%update fn to visualize with color
function handles = updateVisualFn(fn, b_correctFnIndex, b_fn_under_min, handles)

%Update number
handles.actual_fn.String = num2str(fn);

%Update color
if(b_fn_under_min)
    handles.actual_fn.BackgroundColor = [0 0 1]; %blue
elseif( b_correctFnIndex )
    handles.actual_fn.BackgroundColor = [0 1 0]; %green 
else
    handles.actual_fn.BackgroundColor = [1 0 0]; %red
end

%Add a point to the plots
function handles = plotSinglePoint(target_norm, handles)

    handles.lastSinglePointPlotted = target_norm;
    
    hold(handles.MainPlot,'on')
    plot(handles.MainPlot, target_norm(1) , target_norm(2),'r*');
    %plot(handles.MainPlot, target_norm(2) , -target_norm(1),'r*');
    
    hold(handles.plot_xm,'on')
    plot(handles.plot_xm, target_norm(1), target_norm(3),'r*');
    %plot(handles.plot_xm, target_norm(2), target_norm(3),'r*');

    hold(handles.plot_ym,'on')
    plot(handles.plot_ym, target_norm(3), target_norm(2), 'r*');
    %plot(handles.plot_ym, target_norm(3), -target_norm(1), 'r*');

    
    hold(handles.plot3d,'on')
    plot3(handles.plot3d, target_norm(1), target_norm(2), target_norm(3),'r*'); 
    
    
%Update the actual point
function update_ActualPoint(hObject,eventdata,hfigure)

    handles = guidata(hfigure);
    
    if isfield(handles,'lastSinglePointPlotted') && isfield(handles,'h_xy') && isfield(handles,'h_xm') && isfield(handles,'h_ym')
    
        if all( isvalid([handles.h_xy handles.h_xm handles.h_ym]) )
        
            target_norm = gather(handles.lastSinglePointPlotted);

            handles.h_xy.XData = target_norm(1);
            handles.h_xy.YData = target_norm(2);
            %handles.h_xy.XData = target_norm(2);
            %handles.h_xy.YData = -target_norm(1);
            %uistack(handles.h_xy,'top');

            handles.h_xm.XData = target_norm(1);
            handles.h_xm.YData = target_norm(3);
            %handles.h_xm.XData = target_norm(2);
            %handles.h_xm.YData = target_norm(3);
            %uistack(handles.h_xm,'top');


            handles.h_ym.XData = target_norm(3);
            handles.h_ym.YData = target_norm(2);
            %handles.h_ym.XData = target_norm(3);
            %handles.h_ym.YData = -target_norm(1);
            %uistack(handles.h_ym,'top');

            guidata(hfigure, handles);
        end
    end

       
    
function update_timer_refresh(hObject,eventdata,hfigure)
    handles = guidata(hfigure);
    
    if(handles.count_to_refresh <= 0)
        refresh_all(hfigure, handles); 
    end
    

% -- timer callbk
function update_timer(hObject,eventdata,hfigure)
% Timer timer1 callback, called each time timer iterates.
% Gets surface Z data, adds noise, and writes it back to surface object.

%try 

handles = guidata(hfigure);

%read msg
calib_msg = handles.ros.subCalib.receive;
%%Uncomment for debug
% calib_msg.Data = [
%    -1.399999976158142
%   -0.800000011920929
%   -7.0000114440918
%    0.013500000350177
%   -0.052999999374151
%    0.0000
%    1;
%   [ 0.077222425937653
%    0.111334471702576
%    0.070639224052429
%    0.009877002239227
%    0.005764405727386
%    0.111045470237732
%    0.153808870315552
%    0.098232183456421
%    0.020048353672028
%   -0.000780150890350
%    0.040231282711029
%    0.077613110542297
%    0.048840692043304
%    0.011328759193420
%    0.000503056049347
%    0.001337964534760
%    0.012641446590424
%    0.009194731712341
%    0.000916774272919
%    0.001843810081482
%   -0.006862046718597
%   -0.006452045440674
%   -0.003214876651764
%   -0.004468481540680
%    0.002725951671600] + handles.offsetVoltages ;
%   1   
% ];

%first parse message & selectUserData(no)
sensor_force_true = calib_msg.Data(handles.ros.wrenchIndex(1:3));
sensor_torque_true = calib_msg.Data(handles.ros.wrenchIndex(4:6));
voltages_raw = calib_msg.Data(handles.ros.voltIndex);
voltages_true = voltages_raw - handles.offsetVoltages;
voltages = voltages_true;
voltages(handles.userData.remove_volts) = 0;
time_volt = calib_msg.Data(handles.ros.timevoltIndex);
time_wrench = calib_msg.Data(handles.ros.timewrenchIndex);

%userData = handles.userData;

%voltages calculations
centroid = calcCentroid(voltages, handles.userData.XX, handles.userData.YY);
%centroid = [centroid(2); -centroid(1)];
zone = findZone(centroid, handles.userData.angle_bound_lines, handles.userData.zone_radius_intervals);
%Plot
indexSelZone = handles.SelectCentroid.Value;
handles = plotCentroid(centroid, zone, handles);
handles.plotVData.actualVoltages = voltages;
handles.plotVData.actualVoltagesTime = time_volt;

%Check if point is good

%check fn intervals
index_interval_Fn_true = findInterval(handles.userData.Fn_interval, abs(sensor_force_true(3)));
b_fn_under_min = abs(sensor_force_true(3)) < handles.userData.Fn_min;
%PLOT / Update visual Fn before check
indexSelFn = handles.SelectFn.Value;
b_correctFnIndex = indexSelFn == index_interval_Fn_true;
handles = updateVisualFn(sensor_force_true(3), b_correctFnIndex, b_fn_under_min, handles);
if b_fn_under_min || isnan(index_interval_Fn_true) || isnan(zone)
    guidata(hfigure, handles);
    return; %bad data out of interval
end

%check LS limits
%calc Trasform
% % cont_T_sc = computeTransform(centroid, handles.userData.sf_radius, handles.userData.sc_z_sf);
%contact wrench
% % [contact_force_true, contact_torque_true] = rotateWrench(sensor_force_true , sensor_torque_true , cont_T_sc);

% % maxFt_true = getMaxFt(contact_force_true(3),handles.userData.mu_);
% % maxM_true = getMaxM(contact_force_true(3),handles.userData.alpha_, handles.userData.gamma_);

% % target_norm_true = [contact_force_true(1)/maxFt_true , contact_force_true(2)/maxFt_true, contact_torque_true(3)/maxM_true];

% bad data
% % if( norm(target_norm_true) >= 1 )
% %     guidata(hfigure, handles); %bad data out of limit surface
% %     return
% % end
%OK the point is good

%Calc plot point

fn_nomin = handles.dependentData.central_Fn_vect(index_interval_Fn_true);

zoneTrasform = handles.zoneTrasform{zone};
[contact_force_nomin, contact_torque_nomin] = rotateWrench(sensor_force_true , sensor_torque_true , zoneTrasform);
contact_fz_nomin = zoneTrasform(3,1:3) * [0;0;fn_nomin];
maxFt_nomin = getMaxFt(contact_fz_nomin,handles.userData.mu_);
maxM_nomin = getMaxM(contact_fz_nomin,handles.userData.alpha_, handles.userData.gamma_);
target_norm_nomin = [contact_force_nomin(1)/maxFt_nomin ; contact_force_nomin(2)/maxFt_nomin; contact_torque_nomin(3)/maxM_nomin];

%rotate target_norm_nomin to user visual
target_norm_nomin = visual_rotate(target_norm_nomin);

% Plot point?
plotted = (zone ==  indexSelZone) && b_correctFnIndex;
if plotted
    if ( norm(target_norm_nomin) < handles.sliderRadius.Value )
        handles.count_to_refresh = handles.count_to_refresh - 1;
        handles = plotSinglePoint(target_norm_nomin, handles);
    end
elseif ~(indexSelFn <= index_interval_Fn_true && handles.guiData.b_saveNotPlot)
    guidata(hfigure, handles); %If not save point not plotted
    return
end

%Save point
    handles.userData.target_cell{zone,index_interval_Fn_true} = [handles.userData.target_cell{zone,index_interval_Fn_true} , [sensor_force_true;sensor_torque_true] ];
    handles.userData.target_plot_cell{zone,index_interval_Fn_true} = [handles.userData.target_plot_cell{zone,index_interval_Fn_true} , target_norm_nomin ];
    handles.userData.time_target_cell{zone,index_interval_Fn_true} = [handles.userData.time_target_cell{zone,index_interval_Fn_true} time_wrench];

    handles.userData.input_cell{zone,index_interval_Fn_true} = [handles.userData.input_cell{zone,index_interval_Fn_true} , voltages_true];
    handles.userData.input_raw_cell{zone,index_interval_Fn_true} = [handles.userData.input_raw_cell{zone,index_interval_Fn_true} , voltages_raw];
    handles.userData.time_input_cell{zone,index_interval_Fn_true} = [handles.userData.time_input_cell{zone,index_interval_Fn_true} time_volt];
    
    %Update counts
    if(plotted)
    handles.textSavedPoints.String = num2str(size(handles.userData.target_cell{zone,index_interval_Fn_true},2));
    end

guidata(hfigure, handles);
%  catch me
%     disp( getReport( me, 'extended', 'hyperlinks', 'on' ) )
%  end


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% START USER CODE
% Necessary to provide this function to prevent timer callback
% from causing an error after GUI code stops executing.
% Before exiting, if the timer is running, stop it.
clearTimers(handles,false);
% END USER CODE

% Hint: delete(hObject) closes the figure
delete(hObject);


% --- Executes on button press in saveButton.
function saveButton_Callback(hObject, eventdata, handles)
% hObject    handle to saveButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

[file,path] = uiputfile({'*.mat'},'Save Experiment Data', [ handles.userData.finger_id '_calib_exp_' datestr(now,'yyyy_mm_dd__HH_MM')] );

if(file == 0)
    return
end

userData = convertFromGPU(handles.userData);

save([path file], 'userData');
warndlg('SAVE OK','saved!')

% save([path file], 'centerZoneRadius','sf_radius', 'sc_z_sf', 'radius_for_zone_trasform' , 'mu_', 'gamma_', 'alpha_', 'Ts', 'Fn_vect', 'Fn_min', ...
%     'Fn_interval', 'offsetVoltages', 'input_cell', 'target_cell', ...
%     'time_target_cell', 'time_input_cell', 'target_plot_cell' );

% --- Executes on button press in ButtonLoad.
function ButtonLoad_Callback(hObject, eventdata, handles)
% hObject    handle to ButtonLoad (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

hObject.Enable = 'off';
en1 = handles.StartButton.Enable;
handles.StartButton.Enable = 'off';
en2 = handles.ButtonCalcOff.Enable;
handles.ButtonCalcOff.Enable = 'off';

[file,path] = uigetfile({'*.mat'},'Load Experiment Data' );

if(file == 0)
    handles.StartButton.Enable = en1;
    handles.ButtonCalcOff.Enable = en2;
    return
end

data = load([path file]);

handles.userData = data.userData;
handles = clearHandles(handles);

% Update handles structure
guidata(hObject, handles);

cla(handles.plotCentroid)
handles = refresh_all(hObject, handles);

handles.StartButton.Enable = 'on';
handles.StartButton.BackgroundColor = [0 0 1];
handles.StartButton.String = 'Calculate Offset';
hObject.Enable = 'on';

guidata(hObject, handles);


% --- Executes on slider movement.
function sliderRadius_Callback(hObject, eventdata, handles)
% hObject    handle to sliderRadius (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider

handles.plotRadiusValue.String = num2str(hObject.Value);
refresh_all(hObject,handles);


% --- Executes during object creation, after setting all properties.
function sliderRadius_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sliderRadius (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end



function textMu_Callback(hObject, eventdata, handles)
% hObject    handle to textMu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of textMu as text
%        str2double(get(hObject,'String')) returns contents of textMu as a double
mu_ = str2num(hObject.String);
if ~isnan(mu_)
   handles.userData.mu_ = mu_;
   handles = refresh_all(hObject, handles);
   guidata(hObject, handles);
end


% --- Executes during object creation, after setting all properties.
function textMu_CreateFcn(hObject, eventdata, handles)
% hObject    handle to textMu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function editAlpha_Callback(hObject, eventdata, handles)
% hObject    handle to editAlpha (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editAlpha as text
%        str2double(get(hObject,'String')) returns contents of editAlpha as a double
alpha_ = str2num(hObject.String);
if ~isnan(alpha_)
   handles.userData.alpha_ = alpha_;
   handles = refresh_all(hObject, handles);
   guidata(hObject, handles);
end


% --- Executes during object creation, after setting all properties.
function editAlpha_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editAlpha (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function editGamma_Callback(hObject, eventdata, handles)
% hObject    handle to editGamma (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editGamma as text
%        str2double(get(hObject,'String')) returns contents of editGamma as a double
gamma_ = str2num(hObject.String);
if ~isnan(gamma_)
   handles.userData.gamma_ = gamma_;
   handles = refresh_all(hObject, handles);
   guidata(hObject, handles);
end

% --- Executes during object creation, after setting all properties.
function editGamma_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editGamma (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in SelectCentroid.
function SelectCentroid_Callback(hObject, eventdata, handles)
% hObject    handle to SelectCentroid (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns SelectCentroid contents as cell array
%        contents{get(hObject,'Value')} returns selected item from SelectCentroid
refresh_all(hObject, handles);


% --- Executes during object creation, after setting all properties.
function SelectCentroid_CreateFcn(hObject, eventdata, handles)
% hObject    handle to SelectCentroid (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in ButtonCalcOff.
function ButtonCalcOff_Callback(hObject, eventdata, handles)
% hObject    handle to ButtonCalcOff (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

handles.StartButton.Enable = 'off';
handles.ButtonCalcOff.Enable = 'off';
if strcmp(get(handles.timer, 'Running'), 'on')
    errordlg('Main Timer is running!', 'fatal error')
    handles.StartButton.Enable = 'on';
    return
end

handles = calculateOffsetVoltages(handles);
handles.StartButton.Enable = 'on';
handles.ButtonCalcOff.Enable = 'on';
guidata(hObject, handles);


% --- Executes on button press in plotVoltButton.
function plotVoltButton_Callback(hObject, eventdata, handles)
% hObject    handle to plotVoltButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if handles.plotVoltButton %stop plot volt
    if strcmp(get(handles.timer_plotVolt, 'Running'), 'on')
        stop(handles.timer_plotVolt);
    end
    hObject.BackgroundColor = [0 1 0];
    hObject.String = "Start Plot Volt";
    handles.plotVoltButton = false;
    %handles = refresh_all(hObject, handles);
else %start plot volt
    handles.plotVoltButton = true;
    %handles = refresh_all(hObject, handles);
    if strcmp(get(handles.timer_plotVolt, 'Running'), 'off')
        start(handles.timer_plotVolt);
    end
    hObject.BackgroundColor = [1 0 0];
    hObject.String = "Stop Plot Volt";
end

guidata(hObject, handles);


function update_timer_plotVolt(hObject,eventdata,hfigure)
    handles = guidata(hfigure);
    
    handles.plotVoltValues = [handles.plotVoltValues(:,2:end) , handles.plotVData.actualVoltages];
    handles.plotVoltTime = [handles.plotVoltTime(2:end) , handles.plotVData.actualVoltagesTime];
    %handles.plotVoltTime = handles.plotVoltTime - max(handles.plotVoltTime);
    
    handles = plotVoltages(handles);
    
    guidata(hfigure, handles);
    

function handles = plotVoltages(handles)

 cla(handles.axVolt)
 handles.plotVoltsPoints = plot(handles.axVolt, 1:length(handles.plotVoltTime), handles.plotVoltValues,'-+');
 xlabel(handles.axVolt, 'time') , ylabel(handles.axVolt, 'Volts'), grid( handles.axVolt, 'on');
 %view(handles.axVolt,2)

% for i=1:length(handles.plotVoltsPoints)
%     handles.plotVoltsPoints(i).XData = handles.plotVoltTime;
%     handles.plotVoltsPoints(i).YData = handles.plotVoltValues(i,:);
% end
        

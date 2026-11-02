function err=finger_train_plot_compare(t_new,w_new,W_s,b_absolute_error)

    if isempty(b_absolute_error)
        b_absolute_error = false;
    end
    t_new = t_new - t_new(1);
    
    figure
    ax11 = subplot(4,3,1);
    plot(t_new,w_new(:,1),t_new,W_s(1,:));
    title('f_x [N]')
    grid on,
    ax12 = subplot(4,3,4);
    if b_absolute_error
        er = w_new(:,1)-W_s(1,:)';
        tit = 'e sub';
    else
        er = abs(w_new(:,1)-W_s(1,:)')/max(abs(w_new(:,1)))*100;
        title(ax12,'e %')
    end
    plot(t_new,er);
    title(ax12,tit)
    grid on
    %linkaxes([ax1,ax2], 'x');
    
    %figure
    ax21 = subplot(4,3,2);
    plot(t_new,w_new(:,2),t_new,W_s(2,:)),title('f_y [N]'),grid on
    ax22 = subplot(4,3,5);
    if b_absolute_error
        er = w_new(:,2)-W_s(2,:)';
    else
        er = abs(w_new(:,2)-W_s(2,:)')/max(abs(w_new(:,2)))*100;
    end
    plot(t_new,er);
    plot(t_new,er),title('e'),grid on
    %linkaxes([ax1,ax2], 'x');
    
    %figure
    ax31 = subplot(4,3,3);
    plot(t_new,w_new(:,3),t_new,W_s(3,:)),title('f_z [N]'),grid on
    ax32 = subplot(4,3,6);
    if b_absolute_error
        er = w_new(:,3)-W_s(3,:)';
    else
        er = abs(w_new(:,3)-W_s(3,:)')/max(abs(w_new(:,3)))*100;
    end
    plot(t_new,er),title('e'),grid on
    %linkaxes([ax1,ax2], 'x');
    
    %figure
    ax41 = subplot(4,3,7);
    plot(t_new,w_new(:,4),t_new,W_s(4,:)),title('m_x [Nm]'),grid on
    ax42 = subplot(4,3,10);
    if b_absolute_error
        er = w_new(:,4)-W_s(4,:)';
    else
        er = abs(w_new(:,4)-W_s(4,:)')/max(abs(w_new(:,4)))*100;
    end
    plot(t_new,er),title('e'),grid on
    %linkaxes([ax1,ax2], 'x');
    
    %figure
    ax51 = subplot(4,3,8);
    plot(t_new,w_new(:,5),t_new,W_s(5,:)),title('m_y [Nm]'),grid on
    ax52 = subplot(4,3,11);
    if b_absolute_error
        er = w_new(:,5)-W_s(5,:)';
    else
        er = abs(w_new(:,5)-W_s(5,:)')/max(abs(w_new(:,5)))*100;
    end
    plot(t_new,er),title('e'),grid on
    %linkaxes([ax1,ax2], 'x');
    
    %figure 
    ax61 = subplot(4,3,9);
    plot(t_new,w_new(:,6),t_new,W_s(6,:)),title('m_z [Nm]'),grid on
    ax62 = subplot(4,3,12);
    if b_absolute_error
        er = w_new(:,6)-W_s(6,:)';
    else
        er = abs(w_new(:,6)-W_s(6,:)')/max(abs(w_new(:,6)))*100;
    end
    plot(t_new,er),title('e'),grid on
    %linkaxes([ax1,ax2], 'x');
    
    linkaxes([ax11,ax12,ax21,ax22,ax31,ax32,ax41,ax42,ax51,ax52,ax61,ax62], 'x');
    
    disp("var")
    var_ = var(w_new-W_s')
    err=rms(w_new-W_s');
end

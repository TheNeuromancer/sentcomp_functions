def make_filenames(save_path, speed, anomaly, train_times, nb_trial_to_average, decimation, multi_time_points, trial_averaging, sliding_window_for_trial_averaging=False, test_speed=None, position=None, make_folder=True):
    
    if sliding_window_for_trial_averaging == True:
        sliding_window_text = 'sliding_window_'
    else:
        sliding_window_text = ''
    
    if make_folder:
        import os
        if multi_time_points:
            if trial_averaging:
                dir_name = str(nb_trial_to_average) + 'trial_average_' + sliding_window_text + str(train_times['length']) + 'MultiTP_' + str(decimation) + 'decim'
            else:
                dir_name =  'no_trial_average_' + str(train_times['length']) + 'MultiTP_' + str(decimation) + 'decim'
        else:
            if trial_averaging:
                dir_name = str(nb_trial_to_average) + 'trial_average_' + sliding_window_text + 'no_MultiTP_' + str(decimation) + 'decim'
            else:
                dir_name =  'no_trial_average_' + 'no_MultiTP_' + str(decimation) + 'decim'
                
        try:
            os.chdir(save_path)
            os.mkdir(dir_name)
        except: # if the dir is already created just pass
            pass
        if save_path[0] == '/': # whether on my laptop or at neurospin
            dir_name = dir_name + '/' 
        else:
            dir_name = dir_name + '\\' 
    
    
    if multi_time_points:
        if trial_averaging:
            filename = save_path + dir_name + 'GAT_' + speed + '_' + anomaly + '_' + str(nb_trial_to_average) + 'trial_average_' + sliding_window_text + str(train_times['length']) + 'MultiTP_' + str(decimation) + 'decim'
        else:
            filename = save_path + dir_name + 'GAT_' + speed + '_' + anomaly + '_' + str(train_times['length']) + 'MultiTP_' + str(decimation) + 'decim'
    else:
        if trial_averaging:
            filename = save_path + dir_name + 'GAT_' + speed + '_' + anomaly + '_' + str(nb_trial_to_average) + 'trial_average_' + sliding_window_text + str(decimation) + 'decim'
        else:
            filename = save_path + dir_name + 'GAT_' + speed + '_' + anomaly +'_' + str(decimation) + 'decim'
    if test_speed != None:
        filename += '_generalized_to_' + test_speed + str(position) + 'th_pos'
    
    
    filename_diag = filename + '_diagonal.png'
    filename_gat = filename + 'gat.p'
    filename += '.png'
    return filename, filename_diag, filename_gat
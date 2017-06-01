def sentcomp_decoding(subject_name, session, parameter, speed_gen, save_path, epochs_path, stim_data_path, stim_data_path2, speed = '300ms', anomalies = ['string' , 'syntax', 'semantic'], test_speeds = ['160ms', '120ms', '80ms'], blocks = [1,2,3,4,5,6,8], two_blocks = False, two_experiments = True, subject_name2 = subject_name, blocks2 = [1,2,3,4,5,6,7,8], two_blocks2 = False, save = True, decimation=5, n_jobs=1):
    
    import scipy.io as sio
    import numpy as np
    import matplotlib.pyplot as plt
    plt.ion()
    import os
    import mne
    from sklearn import svm
    from mne.decoding import GeneralizationAcrossTime
    from sklearn.cross_validation import StratifiedKFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    from copy import deepcopy
    import pickle
    
    # Personal functions
    from sentcomp_decoding_make_filenames import make_filenames
    from sentcomp_decoding_roc_auc_proba_scorer import roc_auc_proba_scorer
    from sentcomp_make_epochs_function import make_epochs # select the epochs corresponding to wanted condition
    from sentcomp_fuse_epochs_function import fuse_epochs # remove bad channels and concatenate epochs 
    from sentcomp_trial_averaging_function import trial_average


    if speed_gen:
        predict_mode = 'mean-prediction'
    else:
        predict_mode = 'cross-validation'
    
    print("Making correct epochs --------------------- USE ALL POSITIONS ??")
    if two_experiments:
        epochs_correct1 = make_epochs(cond='correct', position=[4,6,8], subject_name=subject_name, session=session+'1', speed_of_interest=speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
        epochs_correct2 = make_epochs(cond='correct', position=[4,6,8], subject_name=subject_name2, session=session+'2', speed_of_interest=speed, blocks=blocks2, decimation=decimation, stim_data_path=stim_data_path2, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks2)
        epochs_correct = fuse_epochs(epochs_correct1, epochs_correct2)
        del epochs_correct1, epochs_correct2
    else:
        epochs_correct = make_epochs(cond='correct', position=[4,6,8], subject_name=subject_name, session=session, speed_of_interest=speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
    
    
    ## Parameters loop
    
    print('Now decoding using parameters ' + str(parameter))
    
    train_times = dict(step=0.01,length=parameter['train_times'])
    test_times = dict(step=0.01,	length=parameter['train_times'])
    
    nb_trial_to_average = parameter['nb_trial_to_average']
    
    multi_time_points = parameter['multi_time_points']
    trial_averaging = parameter['trial_averaging']
    
    if trial_averaging:
        try:
            sliding_window_for_trial_averaging = parameter['sliding_window_for_trial_averaging']
        except:
            print('Do not use a sliding window for trial averagi
        
        # ## go to the next parameter if figure already exists

##   filename, filename_diagonal, dump = make_filenames(save_path, speed, anomaly, train_times, nb_trial_to_average, decimation, multi_time_points, trial_averaging, sliding_window_for_trial_averaging=sliding_window_for_trial_averaging, test_speed=None, position=None)
    # 
    # if os.path.isfile(filename) == True:
    #     print('Already done so go to the next parameter')
    #     continue
    # 
    # if 'epochs' in globals():
    #     del epochs
    
    print(speed + ' ' + anomaly)

    ## Import epochs data
    
    if two_experiments:
        epochs1 = make_epochs(cond=anomaly, position=[4,6,8], subject_name=subject_name, session=session+'1',  speed_of_interest=speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
        epochs2 = make_epochs(cond=anomaly, position=[4,6,8], subject_name=subject_name2, session=session+'2',  speed_of_interest=speed, blocks=blocks2, decimation=decimation, stim_data_path=stim_data_path2, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks2)
        epochs = fuse_epochs(epochs1, epochs2)
        del epochs1, epochs2
    else:
        epochs = make_epochs(cond=anomaly, position=[4,6,8], subject_name=subject_name, session=session, speed_of_interest=speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)

    ## Trial averaging

    if trial_averaging: 
        epochs_averaged, epochs_correct_averaged = trial_average(epochs, epochs_correct, nb_trial_to_average, sliding_window_for_trial_averaging)

    ## Preparing y vector and X data
    
    if trial_averaging:
        X = fuse_epochs(epochs_averaged, epochs_correct_averaged)
        y = np.zeros(len(X))
        y[0:len(epochs_averaged)] = np.ones(len(epochs_averaged))
        
        del epochs_averaged, epochs_correct_averaged
        
    else:
        X = fuse_epochs(epochs, epochs_correct)        
        y = np.zeros(len(X))
        y[0:len(epochs)] = np.ones(len(epochs))
        
        del epochs#, epochs_correct
        
    ## Randomize to check null performance
    # np.random.shuffle(y)
    
    ## Remove EOG channels if not already done
    
    for ch in ['EOG061', 'EOG062']:
        if ch in X.ch_names:
            X.drop_channels([ch])
        
        ## Decoding
    # SVM parameters
    n_fold = 5
    C = 1
    scaler = StandardScaler()
    model = svm.SVC(C=C, kernel='linear', class_weight='balanced', probability=True)
    clf = make_pipeline(scaler, model)
    cv = StratifiedKFold(y, n_fold)
        
    gat = GeneralizationAcrossTime( cv=cv,
                                    clf=clf, 
                                    predict_mode=predict_mode,         
                                    predict_method='predict_proba',
                                    n_jobs=n_jobs,
                                    scorer=roc_auc_proba_scorer,
                                    #score_mode='mean-fold-wise',
                                    train_times=train_times,
                                    test_times=test_times)
    print("Fitting for parameters " + str(parameter))
    gat.fit(X, y)
    
    if speed_gen:
        pass
    else:
        print("Predicting for parameters " + str(parameter))
        y_pred = gat.predict(X)
        
        print("Scoring for parameters " + str(parameter))
        score = gat.score(X, y)
        
        filename, filename_diagonal, filename_gat = make_filenames(save_path, speed, anomaly, train_times, nb_trial_to_average, decimation, multi_time_points, trial_averaging, sliding_window_for_trial_averaging=sliding_window_for_trial_averaging, test_speed=None, position=None)
        
        gat.plot(vmin=.4, vmax=.8, show=False)
        # plt.show()
        # plt.pause(.0001)
        if save:
            plt.savefig(filename)
        gat.plot_diagonal(chance=.5, show=False)
        # plt.show()
        # plt.pause(.0001)
        if save:
            plt.savefig(filename_diagonal)  
        plt.close('all')
        pickle.dump(gat.scores_, open(filename_gat, "wb" ), 2)
        
        if not speed_gen:
            del gat
    
    ## Generalize to faster speeds        print('ok') 
    
    if speed_gen:
        
        for test_speed in test_speeds:
            
            for position in [[4,6,8],4,6,8]:
                
                try:
                
                ## go to the next parameter if figure already exists
            
                    filename, filename_diagonal, dump = make_filenames(save_path, speed, anomaly, train_times, nb_trial_to_average, decimation, multi_time_points, trial_averaging, sliding_window_for_trial_averaging=sliding_window_for_trial_averaging, test_speed=test_speed, position=position)
                    if os.path.isfile(filename) == True:
                        print('Already done so go to the next parameter')
                        continue
                
                # import epochs
                    if two_experiments:
                        epochs1 = make_epochs(cond=anomaly, position=position, subject_name=subject_name, session=session+'1', speed_of_interest=test_speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
                        epochs2 = make_epochs(cond=anomaly, position=position, subject_name=subject_name, session=session+'2', speed_of_interest=test_speed, blocks=blocks2, decimation=decimation, stim_data_path=stim_data_path2, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks2)
                        epochs = fuse_epochs(epochs1, epochs2)
                        del epochs1, epochs2
                        
                        epochs_correct1 = make_epochs(cond='correct', position=position, subject_name=subject_name, session=session+'1', speed_of_interest=test_speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
                        epochs_correct2 = make_epochs(cond='correct', position=position, subject_name=subject_name, session=session+'2', speed_of_interest=test_speed, blocks=blocam150105ks2, decimation=decimation, stim_data_path=stim_data_path2, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks2)
                        epochs_correct = fuse_epochs(epochs_correct1, epochs_correct2)
                        del epochs_correct1, epochs_correct2

                    else:
                        epochs = make_epochs(cond=anomaly, position=position, subject_name=subject_name, session=session, speed_of_interest=test_speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
                        epochs_correct = make_epochs(cond='correct', position=position, subject_name=subject_name, session=session, speed_of_interest=test_speed, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=True, two_blocks=two_blocks)
                        

                # Trial averaging
                    if trial_averaging:    
                        try:
                            epochs_averaged, epochs_correct_averaged = trial_average(epochs, epochs_correct, nb_trial_to_average, sliding_window_for_trial_averaging)
                        except:
                            continue #exception for not enough trials conditions
                                
                # Preparing y vector and X data
                    if trial_averaging:
                        X = mne.epochs.concatenate_epochs([epochs_averaged, epochs_correct_averaged])
                        y = np.zeros(len(X))
                        y[0:len(epochs_averaged)] = np.ones(len(epochs_averaged))
                        
                        del epochs_averaged, epochs_correct_averaged
                        
                    else:
                        X = mne.epochs.concatenate_epochs([epochs, epochs_correct])        
                        y = np.zeros(len(X))
                        y[0:len(epochs)] = np.ones(len(epochs))
                        
                        del epochs#, epochs_correct
        
                # Decoding
                    y_pred = gat.predict(X)
                    
                    score = gat.score(X, y)
                    
                    filename, filename_diagonal, filename_gat = make_filenames(save_path, speed, anomaly, train_times, nb_trial_to_average, decimation, multi_time_points, trial_averaging, sliding_window_for_trial_averaging=sliding_window_for_trial_averaging, test_speed=test_speed, position=position)
                    
                    gat.plot(vmin=.4, vmax=.8)
                    # plt.show()
                    # plt.pause(.0001)
                    if save:
                        plt.savefig(filename)
                    gat.plot_diagonal(chance=.5)
                    # plt.show()
                    # plt.pause(.0001)
                    if save:
                        plt.savefig(filename_diagonal)  
                    plt.close('all')
                    pickle.dump(gat.scores_, open(filename_gat, "wb" ), 2)
                    del gat
                    
                except:
                    print("Error on the speed_gen")
                    continue
                    
    return
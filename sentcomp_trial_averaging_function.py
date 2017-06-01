import mne
import numpy as np

def trial_average(epochs, epochs_correct, nb_trial_to_average, sliding_window_for_trial_averaging):
    
    if sliding_window_for_trial_averaging:
        
        nb_averaged_trials = len(epochs)
        data = epochs.get_data()
        np.random.shuffle(data)
        indices = list(range(len(data))) * nb_trial_to_average
        np.random.shuffle(indices)
        indices = np.array(indices)
        data = np.array(data)
        data_averaged = []
        
        for itrial_ave in range(nb_averaged_trials):
            average = np.mean(data[[indices[itrial_ave*nb_trial_to_average:itrial_ave*nb_trial_to_average+nb_trial_to_average]]], axis=0)
            # if itrial_ave+nb_trial_to_average <= len(data):
            #     average = np.mean(data[itrial_ave:itrial_ave+nb_trial_to_average], axis=0)
            # else:
            #     average = np.mean(np.concatenate((data[itrial_ave::], data[0:(nb_trial_to_average-len(data[itrial_ave::]))]), axis=0), axis=0)
            data_averaged.append(average)
        epochs_averaged = mne.EpochsArray(data_averaged, info=epochs.info, events=None, tmin=epochs.tmin, event_id=None, reject=None, flat=None, reject_tmin=None, reject_tmax=None, baseline=epochs.baseline, proj=epochs.proj, verbose=None)
        
        nb_averaged_trials_correct = len(epochs_correct)
        data = epochs_correct.get_data()
        np.random.shuffle(data)
        indices = list(range(len(data))) * nb_trial_to_average
        np.random.shuffle(indices)
        data = np.array(data)
        data_averaged = []
        for itrial_ave in range(nb_averaged_trials_correct):
            average = np.mean(data[[indices[itrial_ave*nb_trial_to_average:itrial_ave*nb_trial_to_average+nb_trial_to_average]]], axis=0)
            # if itrial_ave+nb_trial_to_average <= len(data):
            #     average = np.mean(data[itrial_ave:itrial_ave+nb_trial_to_average], axis=0)
            # else:
            #     average = np.mean(np.concatenate((data[itrial_ave::], data[0:(nb_trial_to_average-len(data[itrial_ave::]))]), axis=0), axis=0)
            data_averaged.append(average)
        epochs_correct_averaged = mne.EpochsArray(data_averaged, info=epochs_correct.info, events=None, tmin=epochs_correct.tmin, event_id=None, reject=None, flat=None, reject_tmin=None, reject_tmax=None, baseline=epochs_correct.baseline, proj=epochs_correct.proj, verbose=None)
        
    else:
         
        nb_averaged_trials = len(epochs)//nb_trial_to_average            
        data = epochs.get_data()
        np.random.shuffle(data)
        data_averaged = []
        for itrial_ave in range(nb_averaged_trials):
            average = np.mean(data[itrial_ave*nb_trial_to_average:itrial_ave*nb_trial_to_average+nb_trial_to_average], axis=0)
            data_averaged.append(average)
        epochs_averaged = mne.EpochsArray(data_averaged, info=epochs.info, events=None, tmin=epochs.tmin, event_id=None, reject=None, flat=None, reject_tmin=None, reject_tmax=None, baseline=epochs.baseline, proj=epochs.proj, verbose=None)
        
        nb_averaged_trials_correct = len(epochs_correct)//nb_trial_to_average
        data = epochs_correct.get_data()
        np.random.shuffle(data)
        data_averaged = []
        for itrial_ave in range(nb_averaged_trials_correct):
            average = np.mean(data[itrial_ave*nb_trial_to_average:itrial_ave*nb_trial_to_average+nb_trial_to_average], axis=0)
            data_averaged.append(average)
            # print(np.array(data_averaged).shape)
        epochs_correct_averaged = mne.EpochsArray(data_averaged, info=epochs_correct.info, events=None, tmin=epochs_correct.tmin, event_id=None, reject=None, flat=None, reject_tmin=None, reject_tmax=None, baseline=epochs_correct.baseline, proj=epochs_correct.proj, verbose=None)
        
    return epochs_averaged, epochs_correct_averaged
            
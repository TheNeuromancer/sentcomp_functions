import mne

def check_channels(epochs1, epochs2):
    '''
    Check that 2 epochs have the same channels, and if not drop the channels that are not in common
    '''
    
    ch_names1 = epochs1.ch_names
    ch_names2 = epochs2.ch_names
    
    diff_ch_names1 = [ch for ch in ch_names1 if ch not in ch_names2]
    if diff_ch_names1 != []:
        epochs1.drop_channels(diff_ch_names1)
        print('Dropping channels ' + str(diff_ch_names1) + ' because not in the second epoch')
    
    diff_ch_names2 = [ch for ch in ch_names2 if ch not in ch_names1]
    if diff_ch_names2 != []:
        epochs2.drop_channels(diff_ch_names2)
        print('Dropping channels ' + str(diff_ch_names2) + ' because not in the first epoch')
        
    return epochs1, epochs2
import mne
'''
This function checks that the channels of the epochs from 2 different blocks are compatible (and remove the ones that differ) and then concatenates the epochs.
'''

def fuse_epochs(epochs1, epochs2):
    
    from sentcomp_check_channels_function import check_channels
    
    ## Check that the ch_names match
    
    epochs1, epochs2 = check_channels(epochs1, epochs2)
    
    
    ## if head position is not aligned, continue anyway but raise warning
    
    # if epochs1.info['dev_head_t'].values != epochs2.info['dev_head_t'].values:
    #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    #     print('Head position isn\'t aligned in the 2 epochs')
    #     print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        
    # epochs2.info['dev_head_t'] = None
    # epochs1.info['dev_head_t'] = None
        
    
    
    ## Fuse blocks
    
    epochs_final = mne.concatenate_epochs([epochs1, epochs2])
    
    return epochs_final
    
    
# -*- coding: utf-8 -*-

def make_epochs(cond, position, subject_name, session, speed_of_interest, blocks, decimation, stim_data_path, epochs_path, all_triggers=True, two_blocks=False, save=True, no_second_trigger=False):
    
    import mne
    import scipy.io as sio
    import os
    import numpy as np
    import pickle
    from sentcomp_fuse_epochs_function import fuse_epochs # remove bad channels and concatenate epochs 
    import platform
    
    if platform.system() == 'Windows':
        save_path_epo = 'E:\\Epochs_Repository\\' + subject_name + '\\' 
    else:
        save_path_epo = '/media/tdesbord/LaCie/Epochs_Repository/' + subject_name + '/'
    
    if subject_name == 'Pilote_I_Theo':
        len_block = 120
    elif subject_name == 'Pilote_III_Mat_2':
        len_block = 180
    elif subject_name == 'Pilote_III_Mat':
        len_block = 45
    else:
        len_block = 90
        
    if all_triggers == True: ## all_trigger_string is used to save and load the corresponding epochs
        all_triggers_string = '_all_triggers'
    else:
        all_triggers_string = ''
    
     ## if more than one position, iterate the function
    if isinstance(position, list):
        for pos in position:
            print('\033[1m' + ' Processing position : ' + str(pos))
            epochs_tmp2 = make_epochs(cond=cond, position=pos, subject_name=subject_name, session=session, speed_of_interest=speed_of_interest, blocks=blocks, decimation=decimation, stim_data_path=stim_data_path, epochs_path=epochs_path, all_triggers=all_triggers, two_blocks=two_blocks, no_second_trigger=no_second_trigger)
            if 'epochs' in locals():
                epochs = fuse_epochs(epochs, epochs_tmp2)
            else:
                epochs = epochs_tmp2
        return epochs
    else:
        print('\033[1m' + ' Processing position : ' + str(position))
    
    # Load presentation speed of every block
    try: # If on my Windows laptop
        buffered = open(stim_data_path + '\\speeds.p', "rb")
    except: # if on Unbuntu computer at neurospin
        buffered = open(stim_data_path + 'speeds.p', "rb")
    presentation_speed = pickle.load(buffered) 
    buffered.close()
    for i_block in range(len(presentation_speed)):
        presentation_speed[i_block] = str(presentation_speed[i_block]) + 'ms'
                        
    if two_blocks == True:  # Get the 2 speeds lists when there are 2 parts in the experiment
        try: # If on my Windows laptop
            buffered = open(stim_data_path + '\\speeds2.p', "rb")
        except: # if on Unbuntu computer at neurospin
            buffered = open(stim_data_path + 'speeds2.p', "rb")
        presentation_speed2 = pickle.load(buffered) 
        buffered.close()
        for i_block in range(len(presentation_speed2)):
            presentation_speed2[i_block] = str(presentation_speed2[i_block]) + 'ms'
            
        presentation_speed += presentation_speed2
    
    
    if cond != 'correct' or all_triggers == True: # we do not mark the position of the word when using correct full sentence epochs (if there is an anomaly we put the position in the label
        condition = cond + str(position)
    else:
        condition = cond
        position = '' 
    
    if 'epochs' in globals():
        try:
            del epochs
        except:
            pass
     
    for block in blocks:   
        
        speed = presentation_speed[block-1]
            
        if speed != speed_of_interest: 
            # print(speed)
            continue
        else:
            pass 
            
            ## Look into epochs storage if the segmentation has already been done
        if save:
            try:
                epochs = mne.read_epochs(save_path_epo + 'sentcomp_' + session + '-' + subject_name + '_' + speed_of_interest + '_' + cond + str(position) + all_triggers_string + '-epo.fif')
                print("Retrieving " + save_path_epo + 'sentcomp_' + session + '-' + subject_name + '_' + speed_of_interest + '_'+ cond + str(position) + all_triggers_string + '-epo.fif from memory')
                epochs.decimate(decimation)
                return epochs
            except:
                print()
                print('Failed to get epochs from memory with path ' +  save_path_epo + 'sentcomp_' + session + '-' + subject_name + '_' + speed_of_interest + '_'+ cond + str(position) + all_triggers_string + '-epo.fif. Segmenting the epochs now')
                print()
                pass
    
        print('\033[1m' + '     Processing block : ' + str(block))
            
        ## load data 
        
        try: # If on my Windows laptop
            buffered = open(stim_data_path + 'block' + str(block-1) + '_' + speed + '\\info_stim.p', "rb")
        except: # if on Unbuntu computer at neurospin
            buffered = open(stim_data_path + 'block' + str(block-1) + '_' + speed + '/info_stim.p', "rb")
            
        info_stim = pickle.load(buffered) 
        buffered.close()
        
        # #########################################   
        # if block == 2 and subject_name == 'Pilote_III_Mat_2':
        #     info_stim = info_stim[2::]    
        # 
        # ##########################################
        # if subject_name == 'Pilote_III_Mat':
        #     ind2del = []
        #     for i in range(len(info_stim)):
        #         if i % 2:
        #             ind2del.append(i)
        #     for i in ind2del[::-1]:
        #         del info_stim[i]
        
        subject = '%s%s_block%d_%s' %(session, subject_name, block, speed)
        
        if all_triggers:
            epochs_tmp = mne.read_epochs(epochs_path + 'sentcomp_' + subject + '_all_triggers-epo.fif', preload=True, verbose=False)
        else:
            epochs_tmp = mne.read_epochs(epochs_path + 'sentcomp_' + subject + '-epo.fif', preload=True, verbose=False)
        
        # if 'EOG062' in epochs_tmp.ch_names:
        #     epochs_tmp.drop_channels(['EOG062', 'EOG063'])
            
        # ######################################
        # if subject_name == 'Pilote_I_Theo':
        #     if block == 1:
        #         epochs_tmp.drop(0)
    
 
        if all_triggers:
            ## All triggers
            conditions_tmp = []
            rejected = 0 # numberof rejected sentences
            sentence_index = -1
            word_index = -1
            event_index = -1
            for itrial in range(len(epochs_tmp.drop_log)):
                if 'IGNORED' in epochs_tmp.drop_log[itrial]:
                    continue
                elif 'USER' in epochs_tmp.drop_log[itrial]:
                    continue
                else:
                    word_index += 1
                    if epochs_tmp.drop_log[itrial]: # if rejected then do nothing
                        rejected += 1
                        pass
                    else: # if not, then add the info corresponding to this epochs
                        event_index += 1
                        if epochs_tmp.events[:,2][event_index] == 1 or word_index > 8: # go to the next sentence
                            sentence_index += 1
                            word_index = epochs_tmp.events[:,2][event_index]
                        # if word_index != epochs_tmp.events[:,2][event_index]:
                            # print('Attention !!')
                            # print('Events indices do not match for event ' + str(event_index))
                            # print('/n word_index = ' + str(word_index) + '     trigger event = ' + str(epochs_tmp.events[:,2][event_index]))
                            # print(epochs_tmp.events[:,2][event_index-1:event_index+2])
                            # r = input('press to continue ')
                        if epochs_tmp.events[:,2][event_index-1] == epochs_tmp.events[:,2][event_index]: # if the trigger is repeated according to the trigger events, then we use the word_index
                            conditions_tmp.append(info_stim[sentence_index]['anomaly'] + str(word_index))
                        else: # in all other case it is safer to follow the recorded trigger events
                            conditions_tmp.append(info_stim[sentence_index]['anomaly'] + str(epochs_tmp.events[:,2][event_index]))
                            
                        if info_stim[sentence_index]['anomaly'] != 'correct': # add the anomaly position
                        
                            if no_second_trigger and word_index != (info_stim[sentence_index]['anomaly_position']):
                                conditions_tmp[-1] += '_nottarget'
                            
                            elif not(no_second_trigger) and word_index != (info_stim[sentence_index]['anomaly_position']+1):
                                conditions_tmp[-1] += '_nottarget'
                                
            indice = sentence_index +1
            
        else:
            ## Full sentence epochs
            #sorted by sentence condition
            sentence_index = -1
            conditions_tmp = []
            for i_sent in range(len(info_stim)):
                sentence_index += 1
                conditions_tmp.append(info_stim[i_sent]['anomaly'])
                if info_stim[i_sent]['anomaly'] != 'correct':
                    conditions_tmp[-1] += str(info_stim[i_sent]['anomaly_position']+1)           
             
                    
            # Remove indexes of rejected epochs from 'conditions'
            rejected = []   
            indice = 0
            for itrial in range(len(epochs_tmp.drop_log)):
                if 'IGNORED' in epochs_tmp.drop_log[itrial]:
                    continue
                elif 'USER' in epochs_tmp.drop_log[itrial]:
                    continue
                else:
                    if epochs_tmp.drop_log[itrial]:
                        rejected.append(indice)
                    indice += 1
            
            print('detected ' + str(indice) + 'sentences, ' + str(len(rejected)) + ' are bad so we have ' + str(indice-len(rejected)) +  'sentences')
            
            str_rejected = 'Rejected : '
            
            for i in range(len(rejected)): 
                str_rejected += conditions_tmp[sorted(rejected, reverse=True)[i]] + '-'
                del conditions_tmp[sorted(rejected, reverse=True)[i]]
            print(str_rejected)
            print()
            
                    
                    
        # Check the number of detected sentences
        if indice != len_block:
            print('Attention !! \nNumber of detected sentences doesn\'t match theoretical block length !! \nDetected sentences = ' + str(indice) + '    block length = ' + str(len_block))
            print('rejected : ' + str(rejected))
            print()
            # r = input('Press to continue')
    
        # print(len(conditions_tmp))
        # print(len(info_stim))
        if conditions_tmp[-1][0:4] != info_stim[-1]['anomaly'][0:4]:
            print('Attention !! Problem in the stimuli indexing !')
            print('rejected : ' + str(rejected))
            print('After rejection : ' + conditions_tmp[-1][0:4])
            print('In theory : ' + info_stim[-1]['anomaly'][0:4])
            print('(It is ok if we removed the last compononent of the list)')
            print()
            # r = input('Press to continue')
    
        ## Drop
        
        mask = np.array(conditions_tmp) != condition
        # print((conditions_tmp))
        # print(condition)
        # print(len(epochs_tmp))
        # print(mask.shape)
        epochs_tmp.drop(mask)
        # print(len(epochs_tmp))

        if 'epochs' in locals():
            if 'EOG62' in epochs.info['ch_names']:
                epochs = epochs.drop_channels(['EOG062', 'EOG063'])
            if 'EOG62' in epochs_tmp.info['ch_names']:
                epochs_tmp = epochs_tmp.drop_channels(['EOG062', 'EOG063'])
            # print(len(epochs.info['ch_names']))
            # print(len(epochs_tmp.info['ch_names']))
            epochs = fuse_epochs(epochs, epochs_tmp)
        else:
            epochs = epochs_tmp
    
        print('         nb of epochs = ' + str(sum(np.array(conditions_tmp) == condition)))
        print()
    
    if save :
        try:
            print('Saving epochs to ' + save_path_epo + 'sentcomp_' + session + '-' + subject_name + '_' + speed_of_interest + '_' + cond + str(position) + all_triggers_string + '-epo.fif')
            epochs.save(save_path_epo + 'sentcomp_' + session + '-' + subject_name + '_' + speed_of_interest + '_' + cond + str(position)+ all_triggers_string  + '-epo.fif')
        except:
            print("Could not save epoch")
    
    try:
        epochs.decimate(decimation) 
    except:
        print('decimation failed for block ' + str(blocks))
    
    return epochs
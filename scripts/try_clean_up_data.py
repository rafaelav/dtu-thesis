'''
Created on May 13, 2014

@author: rafa
'''

import sys
sys.path.append( ".." )
from handlers import user_data_handler

#user_list = [1,2,3,6,9,15,17,18,40]
user_list = [6]
start_day = 0
days_to_consider = 1
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5
MIN_PRESENCE_PER_DAY = 10 # apparitions (if they are consecutive it's minimum 5 mins) 
MIN_CONSECUTIVE = 5 # apparitions
MIN_DIST_BETWEEN_APPARITIONS = 2 # mins

def remove_bssids_with_no_influence(bssid_info, days_to_consider):
    """ Removing the bssids that don't appear sufficiently in the given data
    bssid_info - dictionary bssid:[(time, rssi),(time, rssi),...]
    days_to_consider - to know how to consider the minimum required apparitions
    returns dictionary with only needed bssids and a list with the bssids that where ignored
    """
    to_ignore = []
    for key in bssid_info:
        max_consecutive = 0
        consecutive = 0
        #sequence = []
        previous_time = bssid_info[key][0][0]
        #print("START")
        for x in bssid_info[key]:
            if  x[0]-previous_time < MIN_DIST_BETWEEN_APPARITIONS*60:
                consecutive = consecutive + 1
                #sequence.append(x[0])
                #print(x[0],previous_time)
                previous_time = x[0]                
            else:
                #print(sequence, consecutive)
                if consecutive > max_consecutive:
                    max_consecutive = consecutive
                #print("START")
                previous_time = x[0]
                consecutive = 1
                #sequence = [x[0]]
        if consecutive > max_consecutive:
            max_consecutive = consecutive

        #print(sequence, consecutive)

        
        if max_consecutive < MIN_CONSECUTIVE and len(bssid_info[key]) < MIN_PRESENCE_PER_DAY*days_to_consider:
            to_ignore.append(key)

    for bssid in to_ignore:
        #print(x,len(bssid_info[x]))
        del bssid_info[bssid]
    print(len(to_ignore), len(bssid_info.keys()))
    return bssid_info, to_ignore

def discard_not_needed_bssid(user_data, to_ignore):
    """ Gets user data entries and a list of bssids to discard. Returns data entries from which 
    eliminates the ones related to the bssids to doscard"""
    updated_data = []
    for line in user_data:
        if line[3] not in to_ignore:
            updated_data.append(line)
    return updated_data
for user in user_list:
    user_file_name = "user_"+str(user)+"_sorted"
    # get data with noise removed (classic)
    user_data = user_data_handler.retrieve_data_from_user(user_file_name, start_day, days_to_consider)
    print("Data after cleaning noise (clasic): "+str(len(user_data)))
    #print(user_data[1])
    bssid_info = user_data_handler.get_bssid_info_from_data(user_data)
    print(len(bssid_info.keys()))
    #print(bssid_info.keys())
    print(bssid_info[2932])
    bssid_info_1 = dict()
    bssid_info_1[2932]=bssid_info[2932]
    print(len(bssid_info.keys()))
    bssid_info, to_ignore = remove_bssids_with_no_influence(bssid_info, days_to_consider)
    print(len(bssid_info.keys()))
    print(to_ignore)
    user_data = discard_not_needed_bssid(user_data, to_ignore)
    print("Data after cleaning noise (extra): "+str(len(user_data)))

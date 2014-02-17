'''
Created on Feb 17, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from scripts import polaris
sys.path.append( ".." )
from handlers import user_data_handler

def get_different_locations(user_file,start_day,days_to_consider,n_best_signal_bssids,m_most_popular_bssids):
    """Returns the number of locations idetified in user_file data from the start_day for a period of days_to_consider (if days_to_consider is -1, it takes all days in file). If n_best_signal != -1, will only consider the bssids with best signal for each timestamp. Only creates fingerprints for most common bssids in the data interval (if m_most_common!=-1)"""
    # get data from file
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)
    print(user_data[0][1], user_data[len(user_data)-1][1])
    
    # get unique timestamps from data
    timestamps = user_data_handler.get_unique_timestamps(user_data)    
    
    # find out which are the bssids which appear most common ( first m_most_popular_bssids)
    most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
    
    # get fingerprints from file
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps, n_best_signal_bssids, most_common_bssids)

    # sort fingerprints based on timestamp
    fingerprint_list = []
    keylist = fingerprints.keys()
    keylist.sort()
    for key in keylist:
        fingerprint_list.append((key, fingerprints[key]))
    
    # identify locations
    l_count = 0
    i = 0
    while i < len(fingerprint_list)-1:
        location = []
        location_times = []
        location.append(fingerprint_list[i])
        location_times.append(fingerprint_list[i][0])
        j = i + 1
        while j < len(fingerprint_list) and polaris.get_fingerprint_similarity(fingerprint_list[i][1], fingerprint_list[j][1]) > 0.95:
            #print(fingerprint_list[j-1][1],"\n",fingerprint_list[j][1])
            location.append(fingerprint_list[j])
            location_times.append(fingerprint_list[j][0])
            j = j + 1
        i = j # moving to next location which seems to start at j
        if len(location_times) > 5:
            l_count = l_count + 1
            print("Loc: "+str(l_count)+"\n",location_times)
    
    return l_count

get_different_locations("user_1_sorted",0,1,-1,10)
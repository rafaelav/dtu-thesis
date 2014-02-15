'''
Created on Feb 10, 2014

@author: rafa
'''
import io
import random
from objects.AccessPoint import AccessPoint

MIN_RSSI = -99
MAX_RSSI = -50

DAY_INTERVAL_SECS = 24*60*60

def retrieve_data_from_user(user_file_name, start_day, days_to_consider):
#    fingerprint_list = []
    user_data = []
    with io.open('../{0}'.format(user_file_name), encoding='utf-8') as f:
        first_registered_time_of_day = 0 
        first_registered_timestamp = 0
        for line in f:
            split_line = line.split()
            if split_line:
                split_line = [int(i) for i in split_line]
            # finding first registered moment
            if first_registered_timestamp == 0 :
                first_registered_timestamp = split_line[1]
            
            # finding first moment of wanted day
            if first_registered_time_of_day == 0:
                if split_line[1] - first_registered_timestamp >= start_day*DAY_INTERVAL_SECS:
                    first_registered_time_of_day = split_line[1]
                    print("First day start time/ Needed day start time: ",first_registered_timestamp, first_registered_time_of_day)
                else:
                    continue
            
            # eliminating the data from Android/iPhone hotspots & buses/trains 
            if split_line[5] not in [1, 6, 7, 8] and split_line[1]-first_registered_time_of_day < days_to_consider * DAY_INTERVAL_SECS:
                user_data.append(split_line)
        return user_data
    
def get_unique_timestamps(data):
    timestamp_list = []
    
    for line in data:
        timestamp = line[1]
        
        if timestamp not in timestamp_list:
            timestamp_list.append(timestamp)
        
    return timestamp_list  

"""def get_unique_bssid(data):
    bssid_list = []
    
    for line in data:
        bssid = line[3]
        
        if bssid not in bssid_list:
            bssid_list.append(bssid)
        
    return bssid_list"""
def get_unique_bssid(fingerprints_dict):
    bssid_list = []
    
    for key in fingerprints_dict:
        for x in fingerprints_dict[key]:
            bssid = x[0]
        
            if bssid not in bssid_list:
                bssid_list.append(bssid)
        
    return bssid_list 


def generate_color_codes_for_bssid(bssid_list):
    """ Returns: dict {bssid: color}"""
    added_colors = []
    bssid_color_list = []
    
    for bssid in bssid_list:
        found = False
        while found == False:
            r = lambda: random.randint(0, 255)
            new_color = '#%02X%02X%02X' % (r(), r(), r())
            # print(new_color)
            if new_color not in added_colors:
                added_colors.append(new_color)
                bssid_color_list.append((bssid, new_color))
                found = True
                # print("found one")
    
    color_dict = dict(bssid_color_list)
    return color_dict

def remove_noise(data):
    final_data = []
    for line in data:
        rssi = line[4]
        if rssi >= MIN_RSSI and rssi <= MAX_RSSI:
            final_data.append(line)
    
    return final_data

def get_most_common_bssids(data, n_most_common):
    most_common = dict()
    
    for line in data:
        bssid = line[3]
        if bssid in most_common.keys():
            most_common[bssid] = most_common[bssid] + 1
        else:
            most_common[bssid] = 1
     
    ordered_list = sorted(most_common.items(), key=lambda x: x[1], reverse=True)
        
    if n_most_common == -1:
        bssids = [] # just bssids
        for x in ordered_list:
            bssids.append(x[0])
        return ordered_list, bssids
    else:
        bssids = [] # just bssids
        for x in ordered_list:
            if len(bssids) < n_most_common:
                bssids.append(x[0])
            else:
                break
        return ordered_list[0:n_most_common], bssids
     
    
            
def get_fingerprints(data, timestamps, n_best_signal, bssids_needed = None):
    """ Returns a dictionari key=timetsamp, value={(bssid, rssi)...} - value contains only first n_best signal APs
    If bssids_needed list is given, then only those bssids will be added to the fingerprints"""
    data = remove_noise(data)
    
    fingerprint_dict = dict()
    
    # create lists for each time stamp (will be used to store each signal
    for ts in timestamps:
        fingerprint_dict[ts] = []
        
    for line in data:
        timestamp = line[1]
        bssid = line[3]
        rssi = line[4]
        
        if bssids_needed is not None:
            if bssid in bssids_needed:
                fingerprint_dict[timestamp].append((bssid, rssi))
        else:
            fingerprint_dict[timestamp].append((bssid, rssi))

    if bssids_needed is not None:
        fingerprint_dict = remove_empty_keys(fingerprint_dict)
        #print("After removing empty keys: ",fingerprint_dict)
        
    selected_dict = get_best_signal(n_best_signal, fingerprint_dict)
    
    return selected_dict

def remove_empty_keys(my_dict):
    for key in my_dict.keys():
        if len(my_dict[key]) == 0:
            my_dict.pop(key, None)
    return my_dict
"""def get_bssids_info_in_time(data, bssids):
    #Returns: a dict which has as keys the identities of APs and values times and strengths of signals at those times
    data = remove_noise(data)
    
    bssids_dict = dict()
    
    # create lists for each time stamp (will be used to store each signal
    for bssid in bssids:
        bssids_dict[bssid] = []
        
    for line in data:
        timestamp = line[1]
        bssid = line[3]
        rssi = line[4]
        # ap = AccessPoint(bssid,rssi)
        
        #TODO - To add access point instead
        bssids_dict[bssid].append((timestamp, rssi))

    return bssids_dict"""
    
def get_bssids_info_in_time(fingerprints_dict, bssids):
    """Returns: a dict which has as keys the identities of APs and values times and strengths of signals at those times"""
    
    bssids_dict = dict()
    
    # create lists for each time stamp (will be used to store each signal
    for bssid in bssids:
        bssids_dict[bssid] = []
        
    for key in fingerprints_dict:
        for x in fingerprints_dict[key]:
            bssid = x[0]
            rssi = x[1]
        
            bssids_dict[bssid].append((key, rssi))

    return bssids_dict

def get_most_popular(n_most_popular, given_dict):
    """ Dictionary signature: {x:[(a1,b1),(a2,b2),(a3,b3)...]; y:[(c1,d1),(c2,d2),(c3,d3),..];...}
        Will return the first n_most_popular which have the most elements in the associated lists
        If n_most_popular is -1 => returns all"""
    if n_most_popular == -1:
        return given_dict
    
    sorted_list = sorted(given_dict.items(), key=lambda x: len(x[1]))
    
    return sorted_list[(0-n_most_popular):]

def get_best_signal(n_best_signal, fingerprint_dict):
    """For each timestamp keeps only the first n_best_signal APs. If requested with -1, returns all"""
    if n_best_signal == -1:
        return fingerprint_dict
    for key in fingerprint_dict.iterkeys():
        ap_list = fingerprint_dict[key] # list of (bssid, rssi) for each timestamp
        sorted_list = sorted(ap_list, key=lambda x: x[1]) # above sorted after rssi values
        # keeping only first n_best_signal from the sorted list
        if len(sorted_list) >= n_best_signal:
            fingerprint_dict[key] = sorted_list[(0-n_best_signal):]
        else:
            fingerprint_dict[key] = sorted_list
    return fingerprint_dict

def get_ordered_time_list(fingerprints):
    time_list = []
    for key in fingerprints.keys():
        time_list.append(key)
    time_list = sorted(time_list, key=lambda x: x)
    return time_list
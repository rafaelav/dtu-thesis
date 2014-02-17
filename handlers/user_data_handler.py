'''
Created on Feb 10, 2014

@author: rafa
'''
import io
import random

MIN_RSSI = -99
MAX_RSSI = -60

DAY_INTERVAL_SECS = 24 * 60 * 60

def retrieve_data_from_user(user_file_name, start_day, days_to_consider):
    """Returns list with list elements where the elements contain: user id, timestamp, ssid bssid rssi context"""
    """ user_file_name - the user data file, start_day - which should be the first day to retrieve data from (calculated as 24h * number from first moment recorded), days_to_consider - for how many cycles of 24 hours from first day to retrieve data"""
    user_data = []
    with io.open('../../wifi_data/{0}'.format(user_file_name), encoding='utf-8') as f:
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
                if split_line[1] - first_registered_timestamp >= start_day * DAY_INTERVAL_SECS:
                    first_registered_time_of_day = split_line[1]
                    #print("First day start time/ Needed day start time: ", first_registered_timestamp, first_registered_time_of_day)
                else:
                    continue
            
            # eliminating the noise and keeping only needed days
            if days_to_consider != -1:
                if not_noise(split_line) and split_line[1] - first_registered_time_of_day < days_to_consider * DAY_INTERVAL_SECS:
                    user_data.append(split_line)
            else:   # all days
                if not_noise(split_line):
                    user_data.append(split_line)
        
        return user_data
    
def get_unique_timestamps(data):
    """Returns list with all unique time values from user data"""
    """data - lines of data from user file"""
    timestamp_list = []
    
    for line in data:
        timestamp = line[1]
        
        if timestamp not in timestamp_list:
            timestamp_list.append(timestamp)
        
    return timestamp_list  

def get_unique_bssid_from_data(data):
    """Returns list with unique bssid from given raw data"""
    bssid_list = []
    
    for line in data:
        bssid = line[3]
        
        if bssid not in bssid_list:
            bssid_list.append(bssid)
        
    return bssid_list

def get_unique_bssid_from_fingerprints(fingerprints_dict):
    """Returns list with unique bssid from given fingerprints dictionary"""
    bssid_list = []
    
    for key in fingerprints_dict:
        for x in fingerprints_dict[key]:
            bssid = x[0]
        
            if bssid not in bssid_list:
                bssid_list.append(bssid)
        
    return bssid_list 


def generate_color_codes_for_bssid(bssid_list):
    """ Returns a dictionary that has as key a bssid and as value an associated auto-generated color for that bssid"""

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

def not_noise(data):
    """ Returns true if the given data doesn't represent noise and false otherwise"""
    rssi = data[4]
    context = data[5]
        
    # if signal not from Android/iPhone hitspot, buses, trains APs
    if context not in [1, 6, 7, 8]:
        # if signal is not considered below or above given noise limits 
        if rssi >= MIN_RSSI and rssi <= MAX_RSSI:
            return True
        else:
            return False
    else:
        return False

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
        bssids = []  # just bssids
        for x in ordered_list:
            bssids.append(x[0])
        return bssids  # ,ordered_list
    else:
        bssids = []  # just bssids
        for x in ordered_list:
            if len(bssids) < n_most_common:
                bssids.append(x[0])
            else:
                break
        return bssids  # ,ordered_list[0:n_most_common]
     
    
            
def get_fingerprints(data, timestamps, n_best_signal, bssids_needed=None):
    """ Returns a dictionary key=timetsamp, value={(bssid, rssi)...} - value contains only first n_best signal APs. If bssids_needed list is given, then only those bssids will be added to the fingerprints"""
    """ data - raw data for user, timestamps - list with unique timestamps, n_best_signal - for each timestamp only first n as best signal are kept, unless it's -1 then all are kept, bssids_needed - in case we only need to consider some bssids and not everything"""
    
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
        
    selected_dict = get_best_signal(n_best_signal, fingerprint_dict)
    
    return selected_dict

def remove_empty_keys(my_dict):
    """Returns the give dictionary from which it discards the keys that were empty"""
    for key in my_dict.keys():
        if len(my_dict[key]) == 0:
            my_dict.pop(key, None)
    return my_dict

    
def get_bssids_info_in_time(fingerprints_dict, bssids):
    """Returns a dictionary that has as keys bssids and for each bssid the value represents a list of tuples (time, rssi) which gives signal of bssid (rssi) at that time"""
    
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
    """ given_dict: {x:[(a1,b1),(a2,b2),(a3,b3)...]; y:[(c1,d1),(c2,d2),(c3,d3),..];...}"""
    """ Returns a dictionary with the first n_most_popular (key,value) elements from the given dictionary. A (key, value) element's popularity is measured by how many tuples (a,b) there are in the value list associated to the key"""
    """ If n_most_popular is -1, returns all"""
    if n_most_popular == -1:
        return given_dict
    
    sorted_list = sorted(given_dict.items(), key=lambda x: len(x[1]))
    
    return sorted_list[(0 - n_most_popular):]

def get_best_signal(n_best_signal, fingerprint_dict):
    """Returns a dictionary extracted from given dictionary such that for each key in the original dictionary (timestamp) it keeps in the value only the first n_best_signal APs (list with best (bssid,rssi))"""
    """If n_best_signal is -1, returns all"""
    if n_best_signal == -1:
        return fingerprint_dict
    for key in fingerprint_dict.iterkeys():
        ap_list = fingerprint_dict[key]  # list of (bssid, rssi) for each timestamp
        sorted_list = sorted(ap_list, key=lambda x: x[1])  # above sorted after rssi values
        
        # keeping only first n_best_signal from the sorted list
        if len(sorted_list) >= n_best_signal:
            fingerprint_dict[key] = sorted_list[(0 - n_best_signal):]
        else:
            fingerprint_dict[key] = sorted_list
    return fingerprint_dict

def get_ordered_time_list(fingerprints):
    """ Returns a list with the keys from the given dictionary (timestamps) ordered ascending"""
    time_list = []
    for key in fingerprints.keys():
        time_list.append(key)
    time_list = sorted(time_list, key=lambda x: x)
    return time_list

"""def remove_noise(data):
    #(Obsolete) Returns data list from which the noise has been eliminated
    final_data = []
    for line in data:
        rssi = line[4]
        context = line[5]
        
        # if signal not from Android/iPhone hitspot, buses, trains APs
        if context not in [1, 6, 7, 8]:
            # if signal is not considered below or above given noise limits 
            if rssi >= MIN_RSSI and rssi <= MAX_RSSI:
                final_data.append(line)
    
    return final_data"""
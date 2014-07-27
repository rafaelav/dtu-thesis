'''
Created on Feb 10, 2014

@author: rafa
'''
import io
import random

MIN_RSSI = -99
MAX_RSSI = -1

DAY_INTERVAL_SECS = 24 * 60 * 60
SEC_IN_MINUTE = 60
MIN_PRESENCE_PER_DAY = 10 # apparitions (if they are consecutive it's minimum 5 mins) 
MIN_CONSECUTIVE = 5 # apparitions
MIN_DIST_BETWEEN_APPARITIONS = 2 # mins

def retrieve_data_from_user(user_file_name, start_day, days_to_consider):
    """Returns list with list elements where the elements contain: user id, timestamp, ssid bssid rssi context"""
    """ user_file_name - the user data file, start_day - which should be the first day to retrieve data from (calculated as 24h * number from first moment recorded), days_to_consider - for how many cycles of 24 hours from first day to retrieve data"""
    user_data = []
    print('../../wifi_data/{0}'.format(user_file_name))
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
        
        # ADDED FOR REMOVING UNNECESSARY BSSIDS AND RELATED INFO
        bssid_info = get_bssid_info_from_data(user_data)
        bssid_info, to_ignore = remove_bssids_with_no_influence(bssid_info, days_to_consider)
        user_data = discard_not_needed_bssid(user_data, to_ignore)
        # END ADDITION
        return user_data

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
            if  x[0]-previous_time < MIN_DIST_BETWEEN_APPARITIONS*SEC_IN_MINUTE:
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

        if max_consecutive < MIN_CONSECUTIVE and len(bssid_info[key]) < MIN_PRESENCE_PER_DAY*days_to_consider:
            to_ignore.append(key)

    for bssid in to_ignore:
        del bssid_info[bssid]

    return bssid_info, to_ignore

def discard_not_needed_bssid(user_data, to_ignore):
    """ Gets user data entries and a list of bssids to discard. Returns data entries from which 
    eliminates the ones related to the bssids to doscard"""
    updated_data = []
    for line in user_data:
        if line[3] not in to_ignore:
            updated_data.append(line)
    return updated_data
    
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

def get_unique_bssid_from_bssid_based_dictionary(bssid_dict):
    """Returns list with unique bssid from given dictionary which has as keys bssids"""
    bssid_list = []
    
    for bssid in bssid_dict.keys():
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

def generate_color_codes_for_gps_loc(stops):
    """ Returns a dictionary that has as key a bssid and as value an associated auto-generated color for that bssid"""

    added_colors = []
    stops_color_list = []
    
    for stop in range(0,len(stops)):
        found = False
        while found == False:
            r = lambda: random.randint(0, 255)
            new_color = '#%02X%02X%02X' % (r(), r(), r())
            # print(new_color)
            if new_color not in added_colors:
                added_colors.append(new_color)
                stops_color_list.append((stop, new_color))
                found = True
                # print("found one")
    
    color_dict = dict(stops_color_list)
    return color_dict

def not_noise(data):
    """ Returns true if the given data doesn't represent noise and false otherwise"""
    if len(data) < 6:
        return False
    
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

def get_bssid_info_from_data(data, only_for_bssid_list=None):
    """Returns a dictionary with bssids as keys and as value for each key a list of tuples (time, rssi) representing each moment at which the bssid has been registered together with the signal strength for that moment. If only_for_bssid_list is present, only these bssids will be keys in the resulting dictionary."""
    if only_for_bssid_list is not None:
        bssid_list = only_for_bssid_list
    else:
        bssid_list = get_unique_bssid_from_data(data)
        
    bssid_dict = dict()
    
    # initiate dictionary
    for bssid in bssid_list:
        bssid_dict[bssid] = []
        
    for line in data:
        bssid = line[3]
        if bssid in bssid_list: #it's either only_for_bssid_list if given or a list with all unique bssids in data
            timestamp = line[1]
            rssi = line[4]
            bssid_dict[bssid].append((timestamp,rssi))       
#         if only_for_bssid_list is not None:
#             if bssid in only_for_bssid_list:
#                 timestamp = line [1]
#                 rssi = line[4]
#                 bssid_dict[bssid].append((timestamp,rssi))
#         else:
#             timestamp = line [1]
#             rssi = line[4]
#             bssid_dict[bssid].append((timestamp,rssi))
            
    
    return bssid_dict
        
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

# NOT USED
def get_bssid_sample_frequency_over_time_bin(bssid_dict, time_bin):
    #Returns a dictionary with the bssid as key and a list of (start_time,end_time,samples) elements representing the number of apperances (samples) of the bssid from start to end time. Start and end should not be more than time_bin minutes apart   
    samples_dict = dict()
    for bssid in bssid_dict.keys():
        print(bssid)
        samples_dict[bssid] = []
        
        start_time = 0
        count = 0
        stop_time = 0
        
        for time_rssi_elem in bssid_dict[bssid]:
            #print(time_rssi_elem)
            if start_time == 0:
                start_time = time_rssi_elem[0]
                count = 1
                stop_time = start_time
                print("Start ",start_time, count, stop_time)
            else:
                #print("limit: ",time_bin * SEC_IN_MINUTE,"Next: ",time_rssi_elem[0])
                if time_rssi_elem[0] - start_time < time_bin * SEC_IN_MINUTE:
                    count = count + 1
                    stop_time = time_rssi_elem[0]
                    #print("Count, possible stop ",count,stop_time)
                else:
                    print("To save: ",start_time,stop_time,count)
                    # add current time_bin stats in result
                    samples_dict[bssid].append((start_time,stop_time,count))
                    # reset count and start time
                    count = 0
                    start_time = 0
                    stop_time = 0
                
        # adding last interval (even if time_bin was not complete
        if count != 0 and start_time != 0:
            #print(start_time,stop_time,count)
            samples_dict[bssid].append((start_time,stop_time,count))
            
    return samples_dict

def get_bssid_sample_frequency_over_time_bin_all(bssid_dict, time_bin, data_start_time, full_data):
    """Returns the dictionary with bssid keys and values as (start_date,end_date,count) given information about needed bssids and the time of first sample in our complete data about a user. The start date is a start of a time_bin, end date is the last aparition of the bssid in the time_bin and count represents number of aparitions of bssid in time_bin"""
    # even when there are 0 samples per time bin
    
    samples_dict = dict()
    count = dict()
    stop_time = dict()

    start_time = data_start_time
    
    for bssid in bssid_dict.keys():
        samples_dict[bssid] = []

        count[bssid] = 0
        stop_time[bssid] = start_time
        
    for line in full_data:
        # need to change time bin
        while line[1]-start_time >=time_bin*SEC_IN_MINUTE:
            # save data
            for bssid in bssid_dict.keys():
                samples_dict[bssid].append((start_time,stop_time[bssid],count[bssid]))
            # update start time
            start_time = start_time + time_bin*SEC_IN_MINUTE
            # reset data
            for bssid in bssid_dict.keys():
                stop_time[bssid] = start_time
                count[bssid] = 0

        # it's a bssid we're interested in
        if line[3] in bssid_dict.keys():
            count[line[3]] = count[line[3]] + 1 
            stop_time[line[3]] = line[1]
            
                        
    # adding last interval (even if time_bin was not complete (if there is last interval)
    found = False
    for bssid in count.keys():
        if count[bssid] != 0:
            found = True
            break
    if found == True:
        for bssid in bssid_dict.keys():
            samples_dict[bssid].append((start_time,stop_time[bssid],count[bssid]))
            
    return samples_dict        

def get_bssid_values_for_rssis_per_time_bins(full_data, bssid_dict, time_bin_len):
    """Returns a dictionary. bssid is key. Each bssid has a list of tuples (start_time_of_bin, [list of rssis in this time bin for current bssid])"""
    """full_data - data for a specific time span. bssid_list - list of bssids we're interested in. time_bin_len - length of the needed time bins"""
    start_time = full_data[0][1]
    
    values_per_bins = dict()    # [bssid] = (start_time, [list of rssi values in the time bin starting from start_time])
    signal_values = dict()      # [bssid] = [list of rssi for current time bin]
        
    for bssid in bssid_dict.keys():
        values_per_bins[bssid] =[]
        signal_values[bssid] = []
        
    unique_timestamps = []

    for line in full_data:
        # need to change time bin
        while line[1]-start_time >=time_bin_len*SEC_IN_MINUTE:
            # save data
            for bssid in bssid_dict.keys():
                #print("here",bssid,signal_values[bssid])
                values_per_bins[bssid].append((start_time, signal_values[bssid], len(unique_timestamps)))
            # update start time
            start_time = start_time + time_bin_len*SEC_IN_MINUTE
            # reset data
            for bssid in bssid_dict.keys():
                signal_values[bssid] = []
            #print(unique_timestamps)
            unique_timestamps = []

        # update time_stamps so that we can calculate average over max possible number of aparitions
        if line[1] not in unique_timestamps:
            unique_timestamps.append(line[1])
        # it's a bssid we're interested in
        if line[3] in bssid_dict.keys():
            signal_values[line[3]].append(line[4]) 

    # adding last interval (even if time_bin was not complete (if there is last interval)
    found = False
    for bssid in signal_values.keys():
        if len(signal_values[bssid]) != 0:
            found = True
            break
    if found == True:
        for bssid in bssid_dict.keys():
            #print("here",bssid,signal_values[bssid])
            values_per_bins[bssid].append((start_time, signal_values[bssid], len(unique_timestamps)))

    return values_per_bins

def get_running_rssi_average_for_time_window(full_data, bssid_dict, time_window):
    """Returns a dictionary. Key: bssid, value: list of elements like (start_time,end_time,avg) representing start time for measurement, end time for mesurement and average value of rssi for bssid in that time span"""
    bssid_rssi_list_dict = dict() # used to keep rssi values for each bssid so that at end of time window can calculate the avg
    bssid_running_avg_dict = dict()
    
    for bssid in bssid_dict.keys():
        bssid_running_avg_dict[bssid] = []
        
    for i in range(0,len(full_data)):
        # reset stuff
        start_time = full_data[i][1]
        #print(start_time)
        crt_i = i
        unique_timestamp = []
        for bssid in bssid_dict.keys():
            bssid_rssi_list_dict[bssid] = []
        
        # get rssi for time_window for each bssid
        while crt_i < len(full_data) and full_data[crt_i][1]-start_time <=time_window*SEC_IN_MINUTE:
            if full_data[crt_i][1] not in unique_timestamp:
                unique_timestamp.append(full_data[crt_i][1])
            if full_data[crt_i][3] in bssid_dict.keys():
                bssid_rssi_list_dict[full_data[crt_i][3]].append(full_data[crt_i][4])
            crt_i = crt_i + 1
        
        for bssid in bssid_dict.keys():
            average = 0

            # list bssid_rssi_list_dict[bssid] contains only non null rssi
            for rssi in bssid_rssi_list_dict[bssid]:
                average = average + rssi
            #print(average)
            #print(unique_timestamp)
            
            # average calculated as sum of non nul values over all rssi (including the ones with val 0 identified in time bin) 
            if len(bssid_rssi_list_dict[bssid]) == 0:
                average_over_non_null_rssi = 0
            else:
                average_over_non_null_rssi = average/len(bssid_rssi_list_dict[bssid])
            
            if len(unique_timestamp) == 0:
                average_over_max_possible_apparitions = 0
            else:
                average_over_max_possible_apparitions = average/len(unique_timestamp)
                
            #print(average_over_non_null_rssi,average_over_max_possible_apparitions)
            bssid_running_avg_dict[bssid].append((start_time, average_over_non_null_rssi,average_over_max_possible_apparitions))
    
    return bssid_running_avg_dict
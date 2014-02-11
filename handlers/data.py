'''
Created on Feb 10, 2014

@author: rafa
'''
import io
import random
from objects.AccessPoint import AccessPoint

MIN_RSSI = -99
MAX_RSSI = -60

def retrieve_data_from_user(user_file_name):
#    fingerprint_list = []
    user_data = []
    
    with io.open('../{0}'.format(user_file_name), encoding='utf-8') as f:
        for line in f:
            split_line = line.split()
            if split_line:
                split_line = [int(i) for i in split_line]
            
            # eliminating the data from Android/iPhone hotspots & buses/trains 
            if split_line[5] not in [1,6,7,8]:
                user_data.append(split_line)
        return user_data
    
def get_unique_timestamps(data):
    timestamp_list = []
    
    for line in data:
        timestamp = line[1]
        
        if timestamp not in timestamp_list:
            timestamp_list.append(timestamp)
        
    return timestamp_list  

def get_unique_bssid(data):
    bssid_list = []
    
    for line in data:
        bssid = line[3]
        
        if bssid not in bssid_list:
            bssid_list.append(bssid)
        
    return bssid_list 

def generate_color_codes_for_bssid(bssid_list):
    added_colors = []
    bssid_color_list = []
    
    for bssid in bssid_list:
        found = False
        while found == False:
            r = lambda: random.randint(0,255)
            new_color = '#%02X%02X%02X' % (r(),r(),r())
            #print(new_color)
            if new_color not in added_colors:
                added_colors.append(new_color)
                bssid_color_list.append((bssid, new_color))
                found = True
                #print("found one")
    
    color_dict = dict(bssid_color_list)
    return color_dict

def remove_noise(data):
    final_data = []
    for line in data:
        rssi = line[4]
        if rssi >= MIN_RSSI and rssi <= MAX_RSSI:
            final_data.append(line)
    
    return final_data
            
def get_fingerprints(data, timestamps):
    data = remove_noise(data)
    
    fingerprint_dict = dict()
    
    # create lists for each time stamp (will be used to store each signal
    for ts in timestamps:
        fingerprint_dict[ts] = []
        
    for line in data:
        timestamp = line[1]
        bssid = line[3]
        rssi = line[4]
        #ap = AccessPoint(bssid,rssi)
        
        """#TODO - To add access point instead"""
        fingerprint_dict[timestamp].append((bssid,rssi))
    
    return fingerprint_dict

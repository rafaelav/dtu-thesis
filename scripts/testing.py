'''
Created on Feb 11, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import data
from scripts import polaris
    
def testing_data_import():
    print("in testing data",1)
    user_data = data.retrieve_data_from_user("user_1",1,1)
    print("\nData:") 
    print(user_data)

def testing_get_unique_timestamps():
    user_data = data.retrieve_data_from_user("user_1",0,1)
    timestamps = data.get_unique_timestamps(user_data)
    print(timestamps)

def testing_get_unique_bssids():
    user_data = data.retrieve_data_from_user("user_1_part",0,1)
    timestamps = data.get_unique_timestamps(user_data)
    fingerprints = data.get_fingerprints(user_data, timestamps,1)
    print(fingerprints)
    bssids = data.get_unique_bssid(fingerprints)
    print(bssids)
    
def testing_generate_color_codes_for_bssid():
    user_data = data.retrieve_data_from_user("user_1",0,1)
    bssids = data.get_unique_bssid(user_data)
    color_codes = data.generate_color_codes_for_bssid(bssids)
    print(color_codes)
    
def testing_remove_noise():
    user_data = data.retrieve_data_from_user("user_1",0,1)
    no_noise_data = data.remove_noise(user_data)
    print(no_noise_data)
    
def testing_get_fingerprints():
    user_data = data.retrieve_data_from_user("user_1",0,1)
    timestamps = data.get_unique_timestamps(user_data)
    
    most_common_with_values, most_common_bssids  = data.get_most_common_bssids(user_data, 10)
    print(most_common_with_values)
    print(most_common_bssids)
    
    #fingerprints = data.get_fingerprints(user_data, timestamps,-1)
    #print("Normal: ",fingerprints)
    fingerprints = data.get_fingerprints(user_data, timestamps, 5, most_common_bssids)
    print(fingerprints)    
    #fingerprints = data.get_fingerprints(user_data, timestamps,1)
    #print(fingerprints)
def testing_calculating_level():
    user_data = data.retrieve_data_from_user("user_1",0,1)
    timestamps = data.get_unique_timestamps(user_data)
    fingerprints = data.get_fingerprints(user_data, timestamps)
    for ts in timestamps:
        fp = fingerprints[ts]
        for (x,y) in fp:
            print(x,y)
            lvl = polaris.get_signal_level(y)
            print(lvl)
def testing_get_signal_similarity():
    print(polaris.get_signal_similarity(-73, -80))
    print(polaris.get_signal_similarity(-83, -90))
    
def testing_get_most_used():
    user_data = data.retrieve_data_from_user("user_1_part",0)
    timestamps = data.get_unique_timestamps(user_data)
    fingerprints = data.get_fingerprints(user_data, timestamps,1)      
    print(fingerprints)     
    bssids = data.get_unique_bssid(fingerprints)
    print(bssids)
    bssid_occurences = data.get_bssids_info_in_time(fingerprints, bssids)
    print(bssid_occurences)
    most_popular = data.get_most_popular(2, bssid_occurences)
    print(most_popular)

def testing_get_most_common_bssids():
    user_data = data.retrieve_data_from_user("user_1",0)
    most_common_with_values, most_common_bssids  = data.get_most_common_bssids(user_data, 1)
    print(most_common_with_values)
    print(most_common_bssids)
    
#print("This is testing")
#testing_data_import()
#testing_get_unique_timestamps()
#testing_get_unique_bssids()
#testing_generate_color_codes_for_bssid()
#testing_remove_noise()
testing_get_fingerprints()
#testing_calculating_level()
#testing_get_signal_similarity()
#testing_get_most_used()
#testing_get_most_common_bssids()
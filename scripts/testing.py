'''
Created on Feb 11, 2014

@author: rafa
'''
from handlers import data
from scripts import polaris
    
def testing_data_import():
    user_data = data.retrieve_data_from_user("user_1")
    print("\nData:") 
    print(user_data)

def testing_get_unique_timestamps():
    user_data = data.retrieve_data_from_user("user_1")
    timestamps = data.get_unique_timestamps(user_data)
    print(timestamps)

def testing_get_unique_bssids():
    user_data = data.retrieve_data_from_user("user_1")
    bssids = data.get_unique_bssid(user_data)
    print(bssids)
    
def testing_generate_color_codes_for_bssid():
    user_data = data.retrieve_data_from_user("user_1")
    bssids = data.get_unique_bssid(user_data)
    color_codes = data.generate_color_codes_for_bssid(bssids)
    print(color_codes)
    
def testing_remove_noise():
    user_data = data.retrieve_data_from_user("user_1")
    no_noise_data = data.remove_noise(user_data)
    print(no_noise_data)
    
def testing_get_fingerprints():
    user_data = data.retrieve_data_from_user("user_1")
    timestamps = data.get_unique_timestamps(user_data)
    fingerprints = data.get_fingerprints(user_data, timestamps)
    print(fingerprints)
def testing_calculating_level():
    user_data = data.retrieve_data_from_user("user_1")
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
#testing_data_import()
#testing_get_unique_timestamps()
#testing_get_unique_bssids()
#testing_generate_color_codes_for_bssid()
#testing_remove_noise()
#testing_get_fingerprints()
#testing_calculating_level()
testing_get_signal_similarity()
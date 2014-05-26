'''
Created on Feb 11, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
from scripts import polaris
from handlers import match_handler
from handlers import location_data_handler
    
def testing_data_import():
    print("in testing data",1)
    user_data = user_data_handler.retrieve_data_from_user("user_1",1,1)
    print("\nData:") 
    print(user_data)

def testing_get_unique_timestamps():
    user_data = user_data_handler.retrieve_data_from_user("user_1",0,1)
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    print(timestamps)

def testing_get_unique_bssids():
    user_data = user_data_handler.retrieve_data_from_user("user_1_part",0,1)
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps,1)
    print(fingerprints)
    bssids = user_data_handler.get_unique_bssid_from_fingerprints(fingerprints)
    print(bssids)
    
def testing_generate_color_codes_for_bssid():
    user_data = user_data_handler.retrieve_data_from_user("user_1",0,1)
    bssids = user_data_handler.get_unique_bssid_from_data(user_data)
    color_codes = user_data_handler.generate_color_codes_for_bssid(bssids)
    print(color_codes)
    
def testing_get_fingerprints():
    user_data = user_data_handler.retrieve_data_from_user("user_1",0,1)
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    
    most_common_with_values, most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, 10)
    print(most_common_with_values)
    print(most_common_bssids)
    
    #fingerprints = data.get_fingerprints(user_data, timestamps,-1)
    #print("Normal: ",fingerprints)
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps, 5, most_common_bssids)
    print(fingerprints)    
    #fingerprints = data.get_fingerprints(user_data, timestamps,1)
    #print(fingerprints)
def testing_calculating_level():
    user_data = user_data_handler.retrieve_data_from_user("user_1",0,1)
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps)
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
    user_data = user_data_handler.retrieve_data_from_user("user_1_part",0)
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps,1)      
    print(fingerprints)     
    bssids = user_data_handler.get_unique_bssid_from_fingerprints(fingerprints)
    print(bssids)
    bssid_occurences = user_data_handler.get_bssids_info_in_time(fingerprints, bssids)
    print(bssid_occurences)
    most_popular = user_data_handler.get_most_popular(2, bssid_occurences)
    print(most_popular)

def testing_get_most_common_bssids():
    user_data = user_data_handler.retrieve_data_from_user("user_1",0)
    most_common_with_values, most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, 1)
    print(most_common_with_values)
    print(most_common_bssids)

def testing_get_ordered_time_list():
    user_data = user_data_handler.retrieve_data_from_user("user_1_part",0,1)
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    
    most_common_with_values, most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, 2)
    print(most_common_with_values)
    print(most_common_bssids)
    
    #fingerprints = data.get_fingerprints(user_data, timestamps,-1)
    #print("Normal: ",fingerprints)
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps, -1, most_common_bssids)
    print(fingerprints)    
    
    ordered_times = user_data_handler.get_ordered_time_list(fingerprints)    
    print(ordered_times)
    
def testing_get_bssid_info_from_data():
    user_data = user_data_handler.retrieve_data_from_user("user_1_part",0,1)
    bssid_dict = user_data_handler.get_bssid_info_from_data(user_data)
    print(bssid_dict)

def testing_get_bssid_sample_frequency_over_time_bin():
    user_data = user_data_handler.retrieve_data_from_user("user_1_sorted",0,1)
    bssid_dict = user_data_handler.get_bssid_info_from_data(user_data)
    samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin(bssid_dict, 5)
    #print(samples_dict)
def testing_get_bssid_sample_frequency_over_time_bin_all():
    user_data = user_data_handler.retrieve_data_from_user("user_1_sorted",0,1)
    most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, 10)
    bssid_dict = user_data_handler.get_bssid_info_from_data(user_data,most_common_bssids)
    data_start_time = user_data[0][1]
    print("Data start: ",data_start_time)
    samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin_all(bssid_dict, 5, data_start_time, user_data)
    print(samples_dict)
def testing_get_bssid_values_for_rssis_per_time_bins():
    user_data = user_data_handler.retrieve_data_from_user("user_1_part",0,1)
    print("got data")
    most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, -1)
    print(most_common_bssids)
    bssid_dict = user_data_handler.get_bssid_info_from_data(user_data,most_common_bssids)
    print(bssid_dict)
    values_dict = user_data_handler.get_bssid_values_for_rssis_per_time_bins(user_data, bssid_dict, 1)
    print(values_dict)
def testing_get_running_rssi_average_for_time_window():
    user_data = user_data_handler.retrieve_data_from_user("user_1_part",0,1)
    print("got data")
    most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, -1)
    print(most_common_bssids)
    bssid_dict = user_data_handler.get_bssid_info_from_data(user_data,most_common_bssids)
    print(bssid_dict)
    running_avg_dict = user_data_handler.get_running_rssi_average_for_time_window(user_data, bssid_dict, 2)
    print(running_avg_dict)
#print("This is testing")
#testing_data_import()
#testing_get_unique_timestamps()
#testing_get_unique_bssids()
#testing_generate_color_codes_for_bssid()
#testing_get_fingerprints()
#testing_calculating_level()
#testing_get_signal_similarity()
#testing_get_most_used()
#testing_get_most_common_bssids()
#testing_get_ordered_time_list()
#testing_get_bssid_info_from_data()
#testing_get_bssid_sample_frequency_over_time_bin_all()
#testing_get_bssid_values_for_rssis_per_time_bins()
#testing_get_running_rssi_average_for_time_window()

def testing_get_data():
    user_data = user_data_handler.retrieve_data_from_user("user_6_sorted", 0, 2)
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]
    after_last = len(user_data)
    print(start_time,end_time, len(user_data))
    
    user_data = user_data_handler.retrieve_data_from_user("user_6_sorted", 2, 2)
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]
    print(start_time,end_time, len(user_data))
    
    user_data = user_data_handler.retrieve_data_from_user("user_6_sorted", 0, 3)
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]
    print(start_time,end_time, len(user_data))
    print(user_data[after_last-1][1])
    print(user_data[after_last][1])
    
    print(user_data[after_last-1])
    print(user_data[after_last])

#testing_get_data()

def testing_combination(filename):
    transitions = location_data_handler.load_pickled_file(filename)
    print(len(transitions))
    print((24*60*30)/5)
    print(max(transitions))

filename = "../../plots/user_6_sorted/star_day_0_step_1_days_30_combined_transitions.p"
testing_combination(filename)
# for i in range(0,30):
#     filename = "../../plots/user_6_sorted/day_"+str(i)+"_count_1_transitions.p"
#     testing_combination(filename, i)
    

    
    
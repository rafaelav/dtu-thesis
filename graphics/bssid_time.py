'''
Created on Feb 14, 2014

@author: rafa
'''
from os import walk

import sys
sys.path.append( ".." )
from handlers import data

import matplotlib.pyplot as plt

def plot_for_bssid(color_to_use, data_to_plot, username, start_day, days_to_consider):
    for key in data_to_plot.iterkeys():
        x_time_list = data_to_plot[key][0]
        y_rssi_list = data_to_plot[key][1]
        # need to sort them
        x_sorted_list = sorted(x_time_list, key=lambda x: x)
        y_sorted_list = sorted(y_rssi_list, key=lambda x: x)
        plt.plot(x_sorted_list, y_sorted_list, color=color_to_use[key], label=key)
        
    plt.title("Access Points - Start (day): "+str(start_day)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("Time", fontsize=10)
    plt.ylabel("Signal strength", fontsize=10)

    plt.legend(loc=2)
    plt.savefig(username+"_plot.png")
    plt.show()

def plot_bssid_over_time(user_file, start_day, days_to_consider, bssid_occurences, colors):
    username = user_file
    
    data_to_plot = dict()
    
    print(bssid_occurences)
    
    for key in bssid_occurences.iterkeys():
        time_list = []
        strength_list = []
        
        for x in bssid_occurences[key]:
            time_list.append(x[0])
            strength_list.append(x[1])
        print(key, time_list, strength_list)
    
        # each bssid will have 2 list (time list and list with strength for bssid at that time)
        data_to_plot[key] = (time_list, strength_list)
    """
    for elem in bssid_occurences_list:
        time_list = []
        strength_list = []
        
        for x in elem[1]:
            time_list.append(x[0])
            strength_list.append(x[1])
        #print(key, time_list, strength_list)
    
        # each bssid will have 2 list (time list and list with strength for bssid at that time)
        data_to_plot[elem[0]] = (time_list, strength_list)"""
        
    plot_for_bssid(colors, data_to_plot, username, start_day, days_to_consider)
    
def prepare_data_and_start_plot(user_file, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids):
    # get data from file
    user_data = data.retrieve_data_from_user(user_file,start_day,days_to_consider)
    #print("Got "+user_file+" data")
    
    # get unique timestamps from data
    timestamps = data.get_unique_timestamps(user_data)
    #print("Got "+user_file+" timestamps")
    
    # find out which are the bssids which appear most common ( first m_most_popular_bssids)
    most_common_with_values, most_common_bssids  = data.get_most_common_bssids(user_data, m_most_popular_bssids)
    
    # git fingerprints which contain only most popular bssids and get only first n_best_signal_bssids for each
    fingerprints = data.get_fingerprints(user_data, timestamps, n_best_signal_bssids, most_common_bssids)
    print("Got "+user_file+" fingerprints")
    print(fingerprints)
    
    # find out bssid which appear in timestamps
    bssids = data.get_unique_bssid(fingerprints)
    print("Got "+user_file+" bssids")
    
    # find out at which times do each bssid appears
    bssid_occurences = data.get_bssids_info_in_time(fingerprints, bssids)
    print("Got "+user_file+" bssid related dictionary")
    
    #most_popular_list = data.get_most_popular(n_most_popular, bssid_occurences)
    
    # get colors for each bssid
    color_codes = data.generate_color_codes_for_bssid(bssids)
    print("Got "+user_file+" colors")
    
    # plot
    plot_bssid_over_time(user_file, start_day, days_to_consider, bssid_occurences, color_codes)
    
prepare_data_and_start_plot("user_1",0,5,5,10)

"""
f = []
for (dirpath, dirnames, filenames) in walk("/home/rafaela/wifi_data"):
    files = f.extend(filenames)
    break

for f in filenames:
    if f == "user_1":
        user_data = data.retrieve_data_from_user(f)
        timestamps = data.get_unique_timestamps(user_data)
        fingerprints = data.get_fingerprints(user_data, timestamps)
        bssids = data.get_unique_bssid(user_data)
        color_codes = data.generate_color_codes_for_bssid(bssids)
        plot_bssi_over_time(f, fingerprints, color_codes)
"""
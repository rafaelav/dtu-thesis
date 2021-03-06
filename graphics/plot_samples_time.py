'''
Created on Jul 16, 2014

@author: rafa
'''

import sys
sys.path.append( ".." )
from handlers import user_data_handler

from graphics import bssids_samples_time_plot

DAY_INTERVAL_SECS = 24 * 60 * 60

def start_plot_bssid_rssi (user_list, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, max_in_legend, plot_interval, time_bin):
    for user in user_list:
        user_file = "user_"+str(user)+"_sorted"
        launch_plot(user_file, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, max_in_legend, days_to_consider*plot_interval, time_bin)

def launch_plot(user_file, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, max_in_legend, plot_time_interval, time_bin):
    """ user_file = username, 
    start_day = from what day to retrieve data(first timestamp means start of first day, 
    days_to_consider = for how many days to retrieve data, 
    n_best_signal_bssids = only consider the ones with best signal
    m_most_popular_bssids = only consider most popular bssids (or max_legend_bssids), 
    max_in_legend = how many bssids to show in legend, 
    plot_time_interval = time at which info about time appears on x axis""" 
    """ Common data """
    # get data from file
    print("Retrieve data from "+user_file)
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)
    print("Retrieved data")
    data_start_time = user_data[0][1]
    data_end_time = data_start_time + days_to_consider * DAY_INTERVAL_SECS#user_data[len(user_data)-1][1]
    print("FOUND TIME CONSTRAINS ",data_start_time,data_end_time)

    most_common_bssids = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
    # find out most popular max_in_legend bssids (the ones who will be put in the plot legend)
    if m_most_popular_bssids > max_in_legend or m_most_popular_bssids == -1:
        most_common_bssids_legend  = user_data_handler.get_most_common_bssids(user_data, max_in_legend)
        # only for max shown in legend we will show plots
        bssid_dict_with_time_and_rssi = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids)
    else:
        most_common_bssids_legend = most_common_bssids
        # only for max shown in legend we will show plots (or most common if those are less)
        bssid_dict_with_time_and_rssi = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids)
     
    # get colors for each bssid
    #color_codes = user_data_handler.generate_color_codes_for_bssid(most_common_bssids)

        # get number of samples based on info we have on bssids (for time_bin)
    bssid_samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin_all(bssid_dict_with_time_and_rssi, time_bin, data_start_time, user_data)
    
    bssid_list = user_data_handler.get_unique_bssid_from_bssid_based_dictionary(bssid_samples_dict)
    
    # get new colors
    colors_dict = user_data_handler.generate_color_codes_for_bssid(bssid_list)
    # plot
    print("Data for user "+user_file+" retrieved. Moving on to preparing the data for plotting...")
    fig_sig_strength = bssids_samples_time_plot.plot_bssid_samples_over_time(user_data, bssid_samples_dict, colors_dict, user_file, days_to_consider, plot_interval, data_start_time, data_end_time)
    fig_sig_strength.clear
user_list = [3]
start_day = 3
days_to_consider = 1
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
days_count = 1
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin_for_sample = 5 # minutes in which samples
start_plot_bssid_rssi(user_list, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, max_in_legend, plot_interval, time_bin_for_sample)
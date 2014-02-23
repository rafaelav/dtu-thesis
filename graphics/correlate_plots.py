'''
Created on Feb 22, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler

import os
from graphics import bssids_signals_time_plot
from graphics import bssids_samples_time_plot

from matplotlib.backends.backend_pdf import PdfPages

def launch_plots(user_file,start_day,days_to_consider, time_bin, n_best_signal_bssids, m_most_popular_bssids, max_in_legend, time_bin_len):
    """ Common data """
    # get data from file
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)
    data_start_time = user_data[0][1]
    data_end_data = user_data[len(user_data)-1][1]

    most_common_bssids = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
    # find out most popular max_in_legend bssids (the ones who will be put in the plot legend)
    if m_most_popular_bssids > max_in_legend or m_most_popular_bssids == -1:
        most_common_bssids_legend  = user_data_handler.get_most_common_bssids(user_data, max_in_legend)
        # only for max shown in legend we will show plots
        bssid_info_bars = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids_legend)
    else:
        most_common_bssids_legend = most_common_bssids
        # only for max shown in legend we will show plots (or most common if those are less)
        bssid_info_bars = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids_legend)
        
    """ Plotting bssid signal in time"""
    # get unique timestamps from data
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    
    # git fingerprints which contain only most popular bssids and get only first n_best_signal_bssids for each
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps, n_best_signal_bssids, most_common_bssids)
    
    # find out bssid which appear in timestamps
    bssids_from_fingerprints = user_data_handler.get_unique_bssid_from_fingerprints(fingerprints)
    
    # find out at which times do each bssid appears
    bssid_occurences = user_data_handler.get_bssids_info_in_time(fingerprints, bssids_from_fingerprints)
    
    # get colors for each bssid
    color_codes = user_data_handler.generate_color_codes_for_bssid(bssids_from_fingerprints)
    
    # plot
    print("Data for user "+user_file+" retrieved. Moving on to preparing the data for plotting...")
    fig_sig_strength = bssids_signals_time_plot.prepared_data_to_plot_for_each_bssid(user_file, start_day, days_to_consider, bssid_occurences, color_codes, most_common_bssids_legend,time_bin_len,data_start_time,data_end_data)#, time_list)


    """ Plotting bssid samples as histograms"""

    # get number of samples based on info we have on bssids (for time_bin)
    bssid_samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin_all(bssid_info_bars, time_bin, data_start_time, user_data)
    
    bssid_list = user_data_handler.get_unique_bssid_from_bssid_based_dictionary(bssid_samples_dict)
    
    # get new colors
    colors_dict = user_data_handler.generate_color_codes_for_bssid(bssid_list)

    # align with colors in plot of signal strength over time
    for bssid in colors_dict.keys():
        if bssid in color_codes.keys():
            colors_dict[bssid] = color_codes[bssid]
    
    # plot bars
    fig_list = bssids_samples_time_plot.plot_bssid_samples_over_time(user_data, bssid_samples_dict, colors_dict, user_file, days_to_consider,time_bin_len,data_start_time,data_end_data)
    
    return fig_sig_strength, fig_list
    
for i in range(1,2):
    username = "user_"+str(i)+"_sorted"
    directory = "../../plots/"+username+"/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    fig_sig_strength, fig_list = launch_plots(username, 0, 1, 5, -1, 10, 10, 60)
    
    for hist_fig in fig_list:
        pp = PdfPages(directory+"signal_strength_and_histograms_"+str(hist_fig[1])+".pdf")
        pp.savefig(fig_sig_strength)
        pp.savefig(hist_fig[0])
        pp.close() 
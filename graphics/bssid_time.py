'''
Created on Feb 14, 2014

@author: rafa
'''
from os import walk
import numpy as np

import sys
from __builtin__ import len
sys.path.append( ".." )
from handlers import data

import matplotlib.pyplot as plt
import datetime

NO_SECS_PER_HOUR = 60*60
HOURS_BETWEEN_TICKS = 2

week   = {0:'Sunday', 1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday',  5:'Friday', 6:'Saturday'}

def get_info_on_time(x_sorted_list):
    text_list = []
    
    for tval in x_sorted_list:
        date_val = datetime.datetime.fromtimestamp(int(tval))
        text_list.append(week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute))
    
    return text_list 

def select_needed(time_list, text_list, pos):
    len_lists = len(time_list)
    crt = 0
    
    if (len_lists%pos)%2 !=0:
        step = len_lists/pos + 1
    else:
        step = len_lists/pos
        
    time_l = []
    text_l = []
    
    while crt < len_lists:
        time_l.append(time_list[crt])
        text_l.append(text_list[crt])
        crt = crt + step
    return time_l, text_l
    

def plot_for_bssid(color_to_use, data_to_plot, username, start_day, days_to_consider):#, time_list):
    """color_to_use - dict with bssid:color, data_to_plot - dict with bssd: ([list_of_time_when_appears],[list_of_strength_at_time])"""
    """username - user for which plotting is done (filename), start_day - day for which plotting starts, days_to_consider - time interval for plot"""
    #"""(NOT USED CURRENTLY) time_list - list with unique time moments found in fingerprints over the days_to_consider starting on start_day interval"""

    """ initial settings for plotting"""
    plt.gcf().set_size_inches(10,2)    
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
        
    """ data editing and plotting for each bssid over the given time"""
    for key in data_to_plot.iterkeys():
        x_time_list = data_to_plot[key][0]
        y_rssi_list = data_to_plot[key][1]
        
        if len(x_time_list)!=len(y_rssi_list):
            print("ERROR!")
            return -1
        
        time_rssi_list = []
        for idx, val in enumerate(x_time_list):
            time_rssi_list.append((val,y_rssi_list[idx]))
        
        # need to sort them
        time_rssi_list = sorted(time_rssi_list, key=lambda x: x[0])
        
        x_sorted_list = []
        y_sorted_list = []
        for elem in time_rssi_list:
            x_sorted_list.append(elem[0])
            y_sorted_list.append(elem[1])
                
        ax.plot(x_sorted_list, y_sorted_list, '-', color=color_to_use[key], label=key)

    # change labels
    locs, labels = plt.xticks()
    ticks_list = ax.xaxis.get_majorticklocs()
    labels = get_info_on_time(ticks_list) # new labels
    plt.xticks(locs, labels)
    
    # Text over plot (title, axes)
    plt.title("Access Points - Start (day): "+str(start_day)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("Moments over time", fontsize=10)
    plt.ylabel("Signal strength", fontsize=10)

    # legend
    handles, labels = ax.get_legend_handles_labels()
    ax = fig.add_subplot(111)
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5,-0.2), ncol=5)
    # end legend
    
    fig.savefig(username+"_plot.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.show()

def plot_bssid_over_time(user_file, start_day, days_to_consider, bssid_occurences, colors):#, time_list):
    username = user_file    
    data_to_plot = dict()
    
    for key in bssid_occurences.iterkeys():
        time_ticks_list = []
        strength_list = []
        
        for x in bssid_occurences[key]:
            time_ticks_list.append(x[0])
            strength_list.append(x[1])
    
        # each bssid will have 2 list (time list and list with strength for bssid at that time)
        data_to_plot[key] = (time_ticks_list, strength_list)
                
    plot_for_bssid(colors, data_to_plot, username, start_day, days_to_consider)#, time_list)
    
def prepare_data_and_start_plot(user_file, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids):
    # get data from file
    user_data = data.retrieve_data_from_user(user_file,start_day,days_to_consider)
    
    # get unique timestamps from data
    timestamps = data.get_unique_timestamps(user_data)
    
    # find out which are the bssids which appear most common ( first m_most_popular_bssids)
    most_common_bssids  = data.get_most_common_bssids(user_data, m_most_popular_bssids)
    
    # git fingerprints which contain only most popular bssids and get only first n_best_signal_bssids for each
    fingerprints = data.get_fingerprints(user_data, timestamps, n_best_signal_bssids, most_common_bssids)
    
    # find out bssid which appear in timestamps
    bssids = data.get_unique_bssid(fingerprints)
    
    # find out at which times do each bssid appears
    bssid_occurences = data.get_bssids_info_in_time(fingerprints, bssids)
    
    # get colors for each bssid
    color_codes = data.generate_color_codes_for_bssid(bssids)
    
    #time_list = data.get_ordered_time_list(fingerprints)
    # plot
    print("Data for user "+user_file+" retrived. Moving on to plotting...")
    plot_bssid_over_time(user_file, start_day, days_to_consider, bssid_occurences, color_codes)#, time_list)
    
prepare_data_and_start_plot("user_1",0,1,-1,10)
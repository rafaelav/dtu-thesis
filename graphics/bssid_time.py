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
    

def plot_for_bssid(color_to_use, data_to_plot, username, start_day, days_to_consider, time_list):
    
    plt.gcf().set_size_inches(10,2)
    
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    
    first = -1
    
    for key in data_to_plot.iterkeys():
        x_time_list = data_to_plot[key][0]
        y_rssi_list = data_to_plot[key][1]
        
        if len(x_time_list)!=len(y_rssi_list):
            print("ERROR!")
            return -1
        
        time_rssi_list = []
        for idx, val in enumerate(x_time_list):
            time_rssi_list.append((x_time_list[idx],y_rssi_list[idx]))
        
        # need to sort them
        time_rssi_list = sorted(time_rssi_list, key=lambda x: x[0])
        
        x_sorted_list = []
        y_sorted_list = []
        for elem in time_rssi_list:
            x_sorted_list.append(elem[0])
            y_sorted_list.append(elem[1])
        
        if first != -1:
            if x_sorted_list[0] < first:
                first = x_sorted_list[0]
        else:
            first = x_sorted_list[0]
        ##widthscale = len(x_sorted_list)/4
        #plt.gcf().set_size_inches(10,2) 
        #figsize = (8*widthscale,2) # fig size in inches (width,height)
        #figure = plt.figure(figsize = figsize) # set the figsize
        
        # get hours and where to plot for time
        # values_list, text_list = get_xticks_info(x_sorted_list)
        
        ax.plot(x_sorted_list, y_sorted_list, '-', color=color_to_use[key], label=key)

    # change labels
    locs, labels = plt.xticks()
    ticks_list = ax.xaxis.get_majorticklocs()
    new_labels = get_info_on_time(ticks_list)
    # UNCOMMENT 2 after only if don't want to see first and last
    #new_labels[0] = ""
    #new_labels[len(new_labels)-1] = ""
    plt.xticks(locs, new_labels)
    plt.title("Access Points - Start (day): "+str(start_day)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("Time", fontsize=10)
    plt.ylabel("Signal strength", fontsize=10)

    # legend
    #plt.legend(loc=8)
    handles, labels = ax.get_legend_handles_labels()
    ax = fig.add_subplot(111)
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5,-0.2), ncol=5)
    # end legend
    
    fig.savefig(username+"_plot.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    #plt.savefig(username+"_plot.png")
    plt.show()

def plot_bssid_over_time(user_file, start_day, days_to_consider, bssid_occurences, colors, time_list):
    username = user_file
    
    data_to_plot = dict()
    
    #print(bssid_occurences)
    
    for key in bssid_occurences.iterkeys():
        time_list = []
        strength_list = []
        
        for x in bssid_occurences[key]:
            time_list.append(x[0])
            strength_list.append(x[1])
        #print(key, time_list, strength_list)
    
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
        
    plot_for_bssid(colors, data_to_plot, username, start_day, days_to_consider, time_list)
    
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
    
    time_list = data.get_ordered_time_list(fingerprints)
    #print(fingerprints)
    
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
    plot_bssid_over_time(user_file, start_day, days_to_consider, bssid_occurences, color_codes, time_list)
    
prepare_data_and_start_plot("user_1",0,1,-1,10)
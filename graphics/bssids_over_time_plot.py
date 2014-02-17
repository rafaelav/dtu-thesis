'''
Created on Feb 14, 2014

@author: rafa
'''

import sys
sys.path.append( ".." )
from handlers import user_data_handler

import matplotlib.pyplot as plt
import datetime

NO_SECS_PER_HOUR = 60*60
HOURS_BETWEEN_TICKS = 2
TIME_BEFORE_INTERRUPT = 60*30 # 30 mins

week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

def get_info_on_time(given_list):
    text_list = []
    
    for tval in given_list:
        date_val = datetime.datetime.utcfromtimestamp(int(tval))
        text_list.append(week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute))
    
    return text_list 

def get_real_times_for_ticklocs(data_to_plot, count):
    """ Returns count timestamps to be ploted on the x axis"""
    timestamps = []
    for key in data_to_plot.iterkeys():
        for tuple_of_lists in data_to_plot[key]: 
            time_list = tuple_of_lists[0]

            for x in time_list:
                if x not in timestamps:
                    timestamps.append(x)
    
    timestamps = sorted(timestamps, key=lambda x: x)
    
    if (len(timestamps)%count)%2 == 0:
        step = len(timestamps)/count
    else:
        step = len(timestamps)/count + 1
    
    #print("First/last timestamps: "+str(timestamps[0])+" "+str(timestamps[len(timestamps)-1]))
    timestamps_to_return = []
    
    crt = 0
    added = 0
    while added < count:
        timestamps_to_return.append(timestamps[crt])
        crt = crt + step
        added = added + 1
    
    #print(timestamps_to_return)
    return timestamps_to_return

def plot_for_bssid(color_to_use, data_to_plot, username, start_day, days_to_consider, most_common_bssids_legend):#, time_list):
    """color_to_use - dict with bssid:color, data_to_plot - dict with bssd: ([list_of_time_when_appears],[list_of_strength_at_time])"""
    """username - user for which plotting is done (filename), start_day - day for which plotting starts, days_to_consider - time interval for plot"""
    #"""(NOT USED CURRENTLY) time_list - list with unique time moments found in fingerprints over the days_to_consider starting on start_day interval"""

    """ initial settings for plotting"""
    # erasing anything from before
    fig = plt.figure(1)
    fig.clear()
    fig.set_size_inches(15,3)    
    
    ax = fig.add_subplot(111)
        
    """ data editing and plotting for each bssid over the given time"""
    for key in data_to_plot.iterkeys():
        first = True
        for list_elements in data_to_plot[key]:
            x_time_list = list_elements[0]
            y_rssi_list = list_elements[1]
            
            if len(x_time_list)!=len(y_rssi_list):
                print("ERROR!")
                return -1
            
            # the first time is the only time when we put a label
            if first == False:
                ax.plot(x_time_list, y_rssi_list, '-', color=color_to_use[key])
            elif first == True and key in most_common_bssids_legend:
                ax.plot(x_time_list, y_rssi_list, '-', color=color_to_use[key], label=key)
                first = False
            elif first == True and key not in most_common_bssids_legend:
                ax.plot(x_time_list, y_rssi_list, '-', color=color_to_use[key])
                first = False

    # change labels
    locs, labels = plt.xticks()
    ticks_list = ax.xaxis.get_majorticklocs()
    count_ticks = len(ticks_list)
    real_moments_ticks = get_real_times_for_ticklocs(data_to_plot, count_ticks)
    labels = get_info_on_time(real_moments_ticks) # new labels
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
    
    fig.savefig("../../plots/"+username+"_"+str(days_to_consider)+"days_plot.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    print("Finished for "+username)
    #plt.show()

def prepared_data_to_plot_for_each_bssid(user_file, start_day, days_to_consider, bssid_occurences, colors, most_common_bssids_legend):#, time_list):
    username = user_file    
    data_to_plot = dict()
    
    for mkey in bssid_occurences.iterkeys():
        time_ticks_list = []
        strength_list = []
        
        data_to_plot[mkey] = []
        
        # sort ocurrences for current bssid based on time
        bssid_occurences[mkey] = sorted(bssid_occurences[mkey], key=lambda x: x[0])
        
        for x in bssid_occurences[mkey]:
            # if first in section or stil part of the same section
            if len(time_ticks_list) == 0 or x[0] - time_ticks_list[len(time_ticks_list)-1] < TIME_BEFORE_INTERRUPT:
                time_ticks_list.append(x[0])
                strength_list.append(x[1])
            else:
                # save the section until here
                data_to_plot[mkey].append((time_ticks_list, strength_list))
                # reset lists
                time_ticks_list = []
                strength_list = []
                # add current
                time_ticks_list.append(x[0])
                strength_list.append(x[1])
                
        # add last section
        # each bssid will have 2 list (time list and list with strength for bssid at that time)
        data_to_plot[mkey].append((time_ticks_list, strength_list))
    
    print("Data for user "+user_file+" prepared for plotting. Moving on to actually plotting...")            
    plot_for_bssid(colors, data_to_plot, username, start_day, days_to_consider, most_common_bssids_legend)#, time_list)
    
def prepare_data_and_start_plot(user_file, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, max_in_legend):
    # get data from file
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)
    
    # get unique timestamps from data
    timestamps = user_data_handler.get_unique_timestamps(user_data)
    
    # find out which are the bssids which appear most common ( first m_most_popular_bssids)
    most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
    
    # find out most popular max_in_legend bssids (the ones who will be put in the plot legend)
    if m_most_popular_bssids > max_in_legend or m_most_popular_bssids == -1:
        most_common_bssids_legend  = user_data_handler.get_most_common_bssids(user_data, max_in_legend)
    else:
        most_common_bssids_legend = most_common_bssids
    # git fingerprints which contain only most popular bssids and get only first n_best_signal_bssids for each
    fingerprints = user_data_handler.get_fingerprints(user_data, timestamps, n_best_signal_bssids, most_common_bssids)
    
    # find out bssid which appear in timestamps
    bssids = user_data_handler.get_unique_bssid_from_fingerprints(fingerprints)
    
    # find out at which times do each bssid appears
    bssid_occurences = user_data_handler.get_bssids_info_in_time(fingerprints, bssids)
    
    # get colors for each bssid
    color_codes = user_data_handler.generate_color_codes_for_bssid(bssids)
    
    #time_list = data.get_ordered_time_list(fingerprints)
    # plot
    print("Data for user "+user_file+" retrieved. Moving on to preparing the data for plotting...")
    prepared_data_to_plot_for_each_bssid(user_file, start_day, days_to_consider, bssid_occurences, color_codes, most_common_bssids_legend)#, time_list)

for i in range(1,2):
    prepare_data_and_start_plot("user_"+str(i)+"_sorted",0,1,-1,-1,10)
#prepare_data_and_start_plot("user_1_sorted",0,1,-1,10)
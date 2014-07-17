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
NO_SECS_PER_MIN = 60
HOURS_BETWEEN_TICKS = 2
TIME_BEFORE_INTERRUPT = 60*2 # 2 mins

week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

# Plot the signals over time with signal strength (connecting dot presence with lines as long as
# there is not more than TIME_BEFORE_INTERRUPT between the dots 

def get_utc_from_epoch(epoch_time):
    date_val = datetime.datetime.utcfromtimestamp(int(epoch_time))
    return week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute)

def get_xticks_xlabels(data_start_time, data_end_time, no_of_ticks, between_ticks):    
    dates_epoch = []
    dates_utc = []
    time_to_add_epoch = data_start_time
    
    added = 0
    while added < no_of_ticks:
        timestamp = time_to_add_epoch
        dates_epoch.append(timestamp)
        dates_utc.append(get_utc_from_epoch(timestamp))
        added = added + 1
        time_to_add_epoch = between_ticks*NO_SECS_PER_MIN + time_to_add_epoch    
    
    # last time stamp
    timestamp = data_end_time
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def plot_for_bssid(color_to_use, data_to_plot, username, start_day, days_to_consider, most_common_bssids_legend, time_bins_len, start_time, end_time):#, time_list):
    """color_to_use - dict with bssid:color, data_to_plot - dict with bssd: ([list_of_time_when_appears],[list_of_strength_at_time])"""
    """username - user for which plotting is done (filename), start_day - day for which plotting starts, days_to_consider - time interval for plot"""
    #"""(NOT USED CURRENTLY) time_list - list with unique time moments found in fingerprints over the days_to_consider starting on start_day interval"""

    """ initial settings for plotting"""
    # erasing anything from before
    fig = plt.figure(1)
    fig.clear()
    fig.set_size_inches(15,5)    
    
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
    no_of_ticks = (end_time - start_time)/(time_bins_len*60) + 1
    print(no_of_ticks)
    ticks, labels_utc = get_xticks_xlabels(start_time,end_time, no_of_ticks, time_bins_len)
        
    ax.set_xlim(start_time-1,end_time+1)
    plt.xticks(ticks, labels_utc, rotation = 90)
    
    # Text over plot (title, axes)
    #plt.title("Access Points - Start (day): "+str(start_day)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("APs presence over time", fontsize=14)
    plt.ylabel("Signal strength", fontsize=14)

    # legend
    handles, labels = ax.get_legend_handles_labels()
    ax = fig.add_subplot(111)
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5,-0.2), ncol=5)
    # end legend
    
    fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_plot.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
    print("Finished for "+username)
    return fig
    #plt.show()

def prepared_data_to_plot_for_each_bssid(user_file, start_day, days_to_consider, bssid_occurences, colors, most_common_bssids_legend, time_bins_len, start_time, end_time):#, time_list):
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
    plotted_fig = plot_for_bssid(colors, data_to_plot, username, start_day, days_to_consider, most_common_bssids_legend, time_bins_len, start_time, end_time)#, time_list)
    return plotted_fig

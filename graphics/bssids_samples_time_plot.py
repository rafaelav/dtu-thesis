'''
Created on Feb 21, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
import datetime
import matplotlib.pyplot as plt
import numpy as np
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

def get_utc_from_epoch(epoch_time):
    date_val = datetime.datetime.utcfromtimestamp(int(epoch_time))
    return week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute)

def get_xticks_xlabels(bin_start_dates, no_of_ticks):
    entries = len(bin_start_dates)
    
    if (entries%no_of_ticks)%2 == 0:
        step = entries/no_of_ticks
    else:
        step = entries/no_of_ticks + 1
    
    dates_epoch = []
    dates_utc = []
    ticks = []
    
    crt = 0
    added = 0
    while added < no_of_ticks:
        timestamp = bin_start_dates[crt]
        ticks.append(crt)
        dates_epoch.append(timestamp)
        dates_utc.append(get_utc_from_epoch(timestamp))
        crt = crt + step
        added = added + 1    
    
    # last time stamp
    timestamp = bin_start_dates[len(bin_start_dates)-1]
    ticks.append(len(bin_start_dates)-1)
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def plot_bssid_samples_over_time(full_data, bssid_samples_dict, colors_dict, username, days_to_consider, time_bins_len, start_time, end_time):
    fig_list = []
    for bssid in bssid_samples_dict:
        values = []
        dates = []
        dates_epoch = []
    
        for elem in bssid_samples_dict[bssid]:
            values.append(elem[2])
            start_time_val = datetime.datetime.utcfromtimestamp(int(elem[0]))
            dates_epoch.append(elem[0])
            dates.append(week[start_time_val.weekday()]+" "+str(start_time_val.hour)+":"+str(start_time_val.minute))
        
        fig = plt.figure()
        fig.clear()
        fig.set_size_inches(15,5)    
        
        print(bssid)
        print(values)
        
#        pos = np.arange(len(dates_epoch))
 #       width = 1.0     # gives histogram aspect to the bar diagram
        
        #plt.xlim([dates_epoch[0],dates_epoch[len(dates_epoch)-1]+time_bin*60])
        """ax = plt.axes()
        ax.set_xticks(pos + (width / 2))
        ax.set_xticklabels(dates, rotation=90, size=6)"""
        """
        # change labels
        locs, labels = plt.xticks()
        ticks_list = fig.xaxis.get_majorticklocs()
        count_ticks = len(ticks_list)
        real_moments_ticks = get_real_times_for_ticklocs(dates_epoch, count_ticks)
        labels = get_info_on_time(real_moments_ticks) # new labels
        plt.xticks(locs, labels)"""

        # to make the 0 values show we make them very close to 0 but positive
        #epsilon = 1e-7
        #values = [x + epsilon for x in values]        

        # Set number of intervals along X axis
#        x_int_num = 10#len(values) - 1
#        plt.locator_params(axis="x", nbins=x_int_num)
        
        # Set X tick labels
        #print(dates)
 #       plt.gca().xaxis.set_ticklabels(dates, rotation = 90)
        width = 200
        print(start_time,end_time)
        no_of_ticks = (end_time - start_time)/(time_bins_len*60) + 1
        print(no_of_ticks)
        ticks, labels_utc = get_xticks_xlabels(dates_epoch, no_of_ticks)
        pos = np.arange(len(dates_epoch))
        #ax = plt.axes()
        #ax.set_xticks(pos + (width / 2))
        #ax.set_xticklabels(labels_utc, rotation=90, size=6)
        
        plt.bar(dates_epoch, values, width, color=colors_dict[bssid])
        plt.xticks(ticks, labels_utc, rotation = 90)
        
        plt.title("Number of samples per time bin for bssid "+str(bssid)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
        plt.xlabel("Time bins", fontsize=10)
        plt.ylabel("Sample count", fontsize=10)        
        fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_plot"+"_"+str(bssid)+"_histo.png")
        fig_list.append((fig,bssid))
    return fig_list
"""        
def prepare_data_to_plot_for_bssid_bars(user_file, start_day, days_to_consider, m_most_popular_bssids, time_bin):
    # get data from file
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)
    
    
    if m_most_popular_bssids != -1:
        # find out which are the bssids which appear most common ( first m_most_popular_bssids)
        most_common_bssids  = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
        #get info about bssids from data
        bssid_info = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids)
    else:
        #get info about bssids from data
        bssid_info = user_data_handler.get_bssid_info_from_data(user_data) # for all bssids in data
        
    #print(bssid_info)
    
    # get number of samples based on info we have on bssids (for time_bin)
#    bssid_samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin(bssid_info, time_bin)
    data_start_time = user_data[0][1]
    bssid_samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin_all(bssid_info, time_bin, data_start_time, user_data)
    
    bssid_list = user_data_handler.get_unique_bssid_from_bssid_based_dictionary(bssid_samples_dict)
    
    colors_dict = user_data_handler.generate_color_codes_for_bssid(bssid_list) 
    
    plot_bssid_samples_over_time(bssid_samples_dict, colors_dict, user_file)
"""
#prepare_data_to_plot_for_bssid_bars("user_1_sorted", 0, 1, 10, 5)
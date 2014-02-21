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

def plot_bssid_samples_over_time(bssid_samples_dict, colors_dict, username):
    for bssid in bssid_samples_dict:
        values = []
        dates = []
    
        for elem in bssid_samples_dict[bssid]:
            values.append(elem[2])
            start_time_val = datetime.datetime.utcfromtimestamp(int(elem[0]))
            dates.append(week[start_time_val.weekday()]+" "+str(start_time_val.hour)+":"+str(start_time_val.minute))
        
        fig = plt.figure()
        
        print(bssid)
        print(values)
        
        pos = np.arange(len(dates))
        width = 1.0     # gives histogram aspect to the bar diagram
        
        ax = plt.axes()
        ax.set_xticks(pos + (width / 2))
        ax.set_xticklabels(dates, rotation=90, size=6)
        
        plt.bar(pos, values, width, color=colors_dict[bssid])
        fig.savefig("../../bars/"+username+"_"+str(bssid)+".png")
        fig.clear()
        
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
    bssid_samples_dict = user_data_handler.get_bssid_sample_frequency_over_time_bin(bssid_info, time_bin)
    
    bssid_list = user_data_handler.get_unique_bssid_from_bssid_based_dictionary(bssid_samples_dict)
    
    colors_dict = user_data_handler.generate_color_codes_for_bssid(bssid_list) 
    
    plot_bssid_samples_over_time(bssid_samples_dict, colors_dict, user_file)

prepare_data_to_plot_for_bssid_bars("user_1_sorted", 0, 3, 10, 5)
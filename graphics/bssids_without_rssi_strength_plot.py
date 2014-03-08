'''
Created on Feb 28, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler

import pickle

import datetime
import matplotlib.pyplot as plt
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

SECS_IN_MINUTE = 60

def get_utc_from_epoch(epoch_time):
    date_val = datetime.datetime.utcfromtimestamp(int(epoch_time))
    return week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute)

def get_xticks_xlabels_from_time(data_start_time, data_end_time, no_of_ticks, between_ticks):    
    dates_epoch = []
    dates_utc = []
    time_to_add_epoch = data_start_time
    
    added = 0
    while added < no_of_ticks:
        timestamp = time_to_add_epoch
        dates_epoch.append(timestamp)
        dates_utc.append(get_utc_from_epoch(timestamp))
        added = added + 1
        time_to_add_epoch = between_ticks*SECS_IN_MINUTE + time_to_add_epoch    
    
    # last time stamp
    timestamp = data_end_time
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def get_start_of_time_bins(start_time,end_time,time_bin):
    start_moments_list = []
    start_moments_list.append(start_time)
    
    while start_time+time_bin*SECS_IN_MINUTE < end_time:
        start_time = start_time + time_bin*SECS_IN_MINUTE
        start_moments_list.append(start_time)
    
    return start_moments_list 
        
def get_bssid_presence_matrix(username, full_data, bssid_dict, time_bin):    
    #used as column name
    column_elements = get_start_of_time_bins(full_data[0][1],full_data[len(full_data)-1][1],time_bin)
    #print(column_elements)
    
    #key is bssid and values is list of 0 and 1 (1 means that the bssid appears in the time bin of the spefici position in list 
    presence_on_rows = dict()
    
    for bssid in bssid_dict.keys():
        presence_on_rows[bssid] = []
        
    for bssid in bssid_dict.keys():    
        bssid_apparition_time_rssi_values = bssid_dict[bssid] # [(time,rssi)....]
        bssid_apparition_time_rssi_values = sorted(bssid_apparition_time_rssi_values, key=lambda x: x[0])
        bssid_apparition_time_list = []
        # getting only times
        for element in bssid_apparition_time_rssi_values:
            bssid_apparition_time_list.append(element[0])
        
        bssid_apparition_time_list = sorted(bssid_apparition_time_list, key=lambda x: x)
        # mark for each column element
        for col_elem in column_elements:
            found = False
            for elem in bssid_apparition_time_list:
                # it appears in time bin
                if elem >= col_elem and elem < col_elem+time_bin*SECS_IN_MINUTE:
                    found = True
                    break
                # already skipped for time bin (so it for sure is not there)
                elif elem >= col_elem+time_bin*SECS_IN_MINUTE:
                    break
            if found == True:
                presence_on_rows[bssid].append(1)
            else:
                presence_on_rows[bssid].append(0)

    #print(presence_on_rows)
    return presence_on_rows, column_elements
        
def prepare_data_for_bssid_without_rssi_strength(user_file, start_day, days_to_consider, m_most_popular_bssids):
    """User file: user_file; From which day to start retrieving data: start_day; For how many days: days_to_consider
    How many bssids (based on their popularity) to take into consideration: m_most_popular_bssids""" 
    # get data from file
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)    
    
    most_common_bssids = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
    bssid_times_and_rssis = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids)
    
    bssid_list = user_data_handler.get_unique_bssid_from_bssid_based_dictionary(bssid_times_and_rssis)
    print("List of found bssids [count = "+str(len(bssid_list))+"]: ",bssid_list)
    # get new colors
    colors_dict = user_data_handler.generate_color_codes_for_bssid(bssid_list)
    
    return user_data, bssid_times_and_rssis, colors_dict

def plot_data(start_time, end_time, plot_time_interval, presence_on_rows, column_elements, color_dict, time_bin, username, days_to_consider):
    values_for_bssids = dict()
    values_list = []
    bssids_list = []
    crt = 1
    for bssid in presence_on_rows.keys():
        values_for_bssids[bssid] = crt
        values_list.append(crt)
        bssids_list.append(bssid)
        crt = crt + 1
    
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)        
    for bssid in bssids_list:
        #print("Something",presence_on_rows[bssid])
        marks_list = presence_on_rows[bssid]
        for i in range(0,len(presence_on_rows[bssid])):
            if marks_list[i] == 1:
                plt.plot([column_elements[i],column_elements[i]+time_bin*SECS_IN_MINUTE - 1], [values_for_bssids[bssid],values_for_bssids[bssid]], '-',linewidth=10, color=color_dict[bssid])
            else:
                plt.plot([column_elements[i],column_elements[i]+time_bin*SECS_IN_MINUTE - 1], [values_for_bssids[bssid],values_for_bssids[bssid]], '-',linewidth=10, color="white")

    plt.ylim(0,len(bssids_list)+1)
    plt.title("Access points without signal strength ("+str(time_bin)+" mins) for bssid "+str(bssid)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("Time bins", fontsize=10)
    plt.ylabel("Names of access points", fontsize=10)    
    
    no_of_ticks = (end_time - start_time)/(plot_time_interval*SECS_IN_MINUTE) + 1
    #print(plot_time_interval,no_of_ticks)
    ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, plot_time_interval)#(dates_epoch, no_of_ticks)
        
    plt.xticks(ticks, labels_utc, rotation = 90)
    plt.yticks(values_list, bssids_list)
    
    fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_no_rssi_plot.png")
def bssid_without_rssi_strength_plot(user_file, start_day, days_to_consider, m_most_popular_bssids, time_bin, plot_time_interval):
    # prepare needed data
    user_data, bssid_times_and_rssis_dict, color_dict = prepare_data_for_bssid_without_rssi_strength(user_file, start_day, days_to_consider, m_most_popular_bssids)
    #print(user_data)
    #print(bssid_times_and_rssis_dict)
    
    # get matrix
    presence_on_rows, column_elements =  get_bssid_presence_matrix(user_file, user_data, bssid_times_and_rssis_dict, time_bin)
    
    print("Need to pickle")
    pickle.dump(presence_on_rows, open("../../plots/"+username+"/"+"pickled_matrix_"+username+"_"+str(days_to_consider)+"days.p", "wb"))
    print("Pickled")
    
    if m_most_popular_bssids == -1:
        limit = 50
        user_data, bssid_times_and_rssis_dict, color_dict = prepare_data_for_bssid_without_rssi_strength(user_file, start_day, days_to_consider, limit)
        presence_on_rows, column_elements =  get_bssid_presence_matrix(user_file, user_data, bssid_times_and_rssis_dict, time_bin)
    
    #print(column_elements)
    #for bssid in presence_on_rows.keys():
    #    print(str(bssid),presence_on_rows[bssid])
    
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]
    plot_data(start_time, end_time, plot_time_interval, presence_on_rows, column_elements, color_dict, time_bin, user_file, days_to_consider)

for i in range(1,3):
    print("For user "+str(i))
    username = "user_"+str(i)+"_sorted"
    start_day = 0
    no_of_days = 2
    most_common = -1
    time_bin = 5
    plot_interval = 60
    bssid_without_rssi_strength_plot(username, start_day, no_of_days, most_common, time_bin, no_of_days*plot_interval)
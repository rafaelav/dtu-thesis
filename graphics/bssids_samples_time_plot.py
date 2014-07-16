'''
Created on Feb 21, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
import datetime
import matplotlib.pyplot as plt
NO_SECS_PER_MIN = 60
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

# Plot number of times a bssid appears in a time bin (used with 5 mins)
def get_utc_from_epoch(epoch_time):
    date_val = datetime.datetime.utcfromtimestamp(int(epoch_time))
    return week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute)

# NOT USED
def get_xticks_xlabels_from_saved_dates(bin_start_dates, no_of_ticks):
    entries = len(bin_start_dates)
    
    if (entries%no_of_ticks)%2 == 0:
        step = entries/no_of_ticks
    else:
        step = entries/no_of_ticks + 1
    
    dates_epoch = []
    dates_utc = []
    #ticks = []
    
    crt = 0
    added = 0
    while added < no_of_ticks:
        timestamp = bin_start_dates[crt]
        #ticks.append(crt)
        dates_epoch.append(timestamp)
        dates_utc.append(get_utc_from_epoch(timestamp))
        crt = crt + step
        added = added + 1    
    
    # last time stamp
    timestamp = bin_start_dates[len(bin_start_dates)-1]
    #ticks.append(len(bin_start_dates)-1)
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

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
        time_to_add_epoch = between_ticks*NO_SECS_PER_MIN + time_to_add_epoch    
    
    # last time stamp
    timestamp = data_end_time
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def plot_bssid_samples_over_time(full_data, bssid_samples_dict, colors_dict, username, days_to_consider, time_bins_len, start_time, end_time):
    fig_list = []
    for bssid in bssid_samples_dict.keys():
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
        
        #print(bssid)
        #print(values)
        
        width = 200
        #print(start_time,end_time)
        no_of_ticks = (end_time - start_time)/(time_bins_len*NO_SECS_PER_MIN) + 1
        #print(no_of_ticks)
        ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, time_bins_len)#(dates_epoch, no_of_ticks)
        
        plt.bar(dates_epoch, values, width, color=colors_dict[bssid])
        plt.xticks(ticks, labels_utc, rotation = 90)
        
        #plt.title("Number of samples per time bin for bssid "+str(bssid)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
        plt.xlabel("Time bins", fontsize=14)
        plt.ylabel("Sample count", fontsize=14)        
        fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_plot"+"_"+str(bssid)+"_histo.png")
        fig_list.append((fig,bssid))
    return fig_list

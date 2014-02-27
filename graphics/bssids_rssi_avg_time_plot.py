'''
Created on Feb 24, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
import datetime
import matplotlib.pyplot as plt
NO_SECS_PER_MIN = 60
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

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
        time_to_add_epoch = between_ticks*NO_SECS_PER_MIN + time_to_add_epoch    
    
    # last time stamp
    timestamp = data_end_time
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def calculate_average_signal_strength(signal_list,max_possible,option):
    count = 0
    
    if option == 1: # sum of non null rssi/ no of non null rssi
        avg_divider = len(signal_list)
    # NOT TO BE USED
    elif option == 2: # the sum of positive values is divided to the number of unique timestamps in bin
        avg_divider = max_possible
    # SAME AS 1
    else: # only take into account the non null vals: [5,0,0,5] = (5 + 5) / 2 = 5
        count = 0
        for s in signal_list:
            if s!= 0:
                count = count + 1
        avg_divider = count
    # no signal in this time bin
#    if len(signal_list) == 0:
#        return 0
    if avg_divider == 0:
        return 0
    
    the_sum = 0
    
    for s in signal_list:
        the_sum = the_sum + s
    
    the_sum = int(the_sum / avg_divider)#len(signal_list))
    
    return the_sum

def plot_bssid_rssi_avg_over_time(full_data, bssid_sig_dict, colors_dict, username, days_to_consider, time_bins_len,option, start_time, end_time):
    fig_list = []
    for bssid in bssid_sig_dict.keys():
        averages = []
        dates = []
        dates_epoch = []
    
        for elem in bssid_sig_dict[bssid]:
            avg = calculate_average_signal_strength(elem[1],elem[2],option)
            averages.append(avg)
            start_time_val = datetime.datetime.utcfromtimestamp(int(elem[0]))
            dates_epoch.append(elem[0])
            dates.append(week[start_time_val.weekday()]+" "+str(start_time_val.hour)+":"+str(start_time_val.minute))
        
        fig = plt.figure()
        fig.clear()
        fig.set_size_inches(15,5)    
        
        print(bssid)
        print(averages)
        
        #width = 200
        print(start_time,end_time)
        no_of_ticks = (end_time - start_time)/(time_bins_len*NO_SECS_PER_MIN) + 1
        print(time_bins_len,no_of_ticks)
        ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, time_bins_len)#(dates_epoch, no_of_ticks)
        
        #plt.bar(dates_epoch, averages, width, color=colors_dict[bssid])
        plt.plot(dates_epoch, averages, 'o-', color=colors_dict[bssid])
        plt.xticks(ticks, labels_utc, rotation = 90)
        
        plt.title("Average signal per time bin for bssid "+str(bssid)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
        plt.xlabel("Time bins", fontsize=10)
        plt.ylabel("Average value", fontsize=10)        
        fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_plot"+"_"+str(bssid)+"_avg_sig.png")
        fig_list.append((fig,bssid))
    return fig_list

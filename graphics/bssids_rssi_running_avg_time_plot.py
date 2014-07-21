'''
Created on Feb 25, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
import datetime
import matplotlib.pyplot as plt
NO_SECS_PER_MIN = 60
MAX_INTERRUPT = 2 # 2 mins
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}
# Running average for various time windows for each bssid
# running average is calcualted as : 
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

def get_only_non_null_data(dates_epoch, averages):
    """Return only the non null averages and associated dates"""
    dates_result = []
    avgs_result = []
    for i in range(0,len(averages)):
        if averages[i] != 0:
            dates_result.append(dates_epoch[i])
            avgs_result.append(averages[i])
    return dates_result,avgs_result

def get_segments_with_no_pause(dates_epoch, averages):
    if len(dates_epoch)!=len(averages):
        print("ERROR! Differnce between length of dates list and averages list")
        
    dates_list = []
    averages_list = []
    crt_avg_strike = []
    crt_dates_strike = []

    crt_avg_strike.append(averages[0])
    crt_dates_strike.append(dates_epoch[0])
        
    for i in range(1,len(dates_epoch)):
        if  dates_epoch[i]-dates_epoch[i-1] < MAX_INTERRUPT * NO_SECS_PER_MIN:
            crt_avg_strike.append(averages[i])
            crt_dates_strike.append(dates_epoch[i])
        else:
            dates_list.append(crt_dates_strike)
            averages_list.append(crt_avg_strike)
            crt_avg_strike = []
            crt_dates_strike = []
            crt_avg_strike.append(averages[i])
            crt_dates_strike.append(dates_epoch[i])
    return dates_list, averages_list
            

def plot_bssid_rssi_avg_over_time(full_data, running_avg_dict, colors_dict, username, days_to_consider, time_bins_len,option,time_window, start_time, end_time):
    fig_list = []
    for bssid in running_avg_dict.keys():
        averages = []
        dates = []
        dates_epoch = []
    
        for elem in running_avg_dict[bssid]:
            if option == 1: # rssi sum / all non_null rssi
                avg = elem[1]
            else:           # rssi sum / all timestamps in bin (max possible apparitions)
                avg = elem[2] 
            averages.append(avg)
            start_time_val = datetime.datetime.utcfromtimestamp(int(elem[0]))
            dates_epoch.append(elem[0])
            dates.append(week[start_time_val.weekday()]+" "+str(start_time_val.hour)+":"+str(start_time_val.minute))
        
        fig = plt.figure()
        fig.clear()
        fig.set_size_inches(15,5)    
        
        #print(bssid)
        #print(averages)
        
        #width = 200
        #print(start_time,end_time)
        no_of_ticks = (end_time - start_time)/(time_bins_len*NO_SECS_PER_MIN) + 1
        #print(time_bins_len,no_of_ticks)
        ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, time_bins_len)#(dates_epoch, no_of_ticks)
        
        dates_epoch_non_null, averages_non_null = get_only_non_null_data(dates_epoch, averages)
        #dates_list, averages_list = get_segments_with_no_pause(dates_epoch,averages)#dates_epoch_non_null, averages_non_null) 
        
        #if len(dates_list) != len(averages_list):
        #    print("ERROR! Not same len for dates and averages lists")
        #    return None
        
        #for i in range(0,len(dates_list)):
        #    if averages_list[i]!=0 :
        #        plt.plot(dates_list[i], averages_list[i], 'D-', color=colors_dict[bssid])
        plt.plot(dates_epoch_non_null, averages_non_null, 'D', color=colors_dict[bssid])
        
        plt.xticks(ticks, labels_utc, rotation = 90)
                    
        #plt.bar(dates_epoch, averages, width, color=colors_dict[bssid])
        """plt.plot(dates_epoch, averages, 'D-', color=colors_dict[bssid])
        plt.xticks(ticks, labels_utc, rotation = 90)"""
        
        #plt.title("Running average signal per time window ("+str(time_window)+" mins) for bssid "+str(bssid)+" Plot over (days): "+str(days_to_consider)+" User: "+username)
        plt.xlabel("Time bins", fontsize=16)
        plt.ylabel("Running average ("+str(time_window)+" mins time window)", fontsize=16)
        fig.tight_layout()        
        fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_plot"+"_"+str(bssid)+"_rn_avg_sig_"+str(time_window)+".png")
        fig_list.append((fig,bssid))
    return fig_list

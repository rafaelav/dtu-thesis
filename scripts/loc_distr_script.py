'''
Created on Aug 1, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
import io
import random
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
import datetime
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

import sys
sys.path.append( ".." )
from handlers import user_data_handler

MIN_RSSI = -99
MAX_RSSI = -1

DAY_INTERVAL_SECS = 24 * 60 * 60
SEC_IN_MINUTE = 60

def retrieve_data_from_user(user_file_name, start_day, days_to_consider):
    """Returns list with list elements where the elements contain: user id, timestamp, ssid bssid rssi context"""
    """ user_file_name - the user data file, start_day - which should be the first day to retrieve data from (calculated as 24h * number from first moment recorded), days_to_consider - for how many cycles of 24 hours from first day to retrieve data"""
    user_data = []
    print('../../location_data/{0}'.format(user_file_name))
    with io.open('../../location_data/{0}'.format(user_file_name), encoding='utf-8') as f:
        first_registered_time_of_day = 0 
        first_registered_timestamp = 0
        
        for line in f:
            split_line = line.split()
            if split_line:
                user = int(split_line[0])
                timestamp = int(split_line[1])
                lat = float(split_line[2])
                lon = float(split_line[3])
                aquracy = float(split_line[4])
                provider = str(split_line[5])
                split_line = [user, timestamp, lat, lon, aquracy, provider]
            # finding first registered moment
            if first_registered_timestamp == 0 :
                first_registered_timestamp = split_line[1]
            
            # finding first moment of wanted day
            if first_registered_time_of_day == 0:
                if split_line[1] - first_registered_timestamp >= start_day * DAY_INTERVAL_SECS:
                    first_registered_time_of_day = split_line[1]
                    #print("First day start time/ Needed day start time: ", first_registered_timestamp, first_registered_time_of_day)
                else:
                    continue
            
            # eliminating the noise and keeping only needed days
            if days_to_consider != -1:
                if split_line[1] - first_registered_time_of_day < days_to_consider * DAY_INTERVAL_SECS:
                    user_data.append(split_line)
            else:   # all days
                user_data.append(split_line)
        
        return user_data

def groupwhile(df, fwhile):
        groups = []
        i = 0
        while i < len(df):
            j = i
            group = []
            while j < len(df) - 1 and fwhile(i, j + 1):
                group.append(j)
                j = j + 1
                
            group.append(j)
            groups.append(group)
            i = j + 1
        
        print(groups)
        return groups


def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        m = 6367000 * c
        return m
    
def getstops_dbscan(user, data):
        group_dist = 70
        min_deltat = 5

        groups = groupwhile(data, lambda start, nxt: haversine(data[start][3],data[start][2],data[nxt][3],data[nxt][2]) <= group_dist) 
        
        stops = []
        for g in groups:
            #print(g)
            start_index = g[0]
            end_index = g[len(g)-1]
            #print(start_index,end_index)
            
            if data[end_index][1] - data[start_index][1] >= min_deltat * SEC_IN_MINUTE:
                stops.append(g)
        
        return stops

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
        time_to_add_epoch = between_ticks*SEC_IN_MINUTE + time_to_add_epoch    
    
    # last time stamp
    timestamp = data_end_time
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def plot_stop_locations(stops, data, start_time, end_time, colors_dict, plot_time_interval, file_path):
    locations_count = len(stops)
    print("Stops identified: ",locations_count, stops)
    
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)       
     
    plt.xlim(start_time,end_time)

    #print(list_locations_over_time_bins)
    crt = 0
    for loc in stops:
        print(loc)
        print(loc[0],loc[len(loc)-1],data[loc[0]][1],data[loc[len(loc)-1]][1])
        s = data[loc[0]][1]
        e = data[loc[len(loc)-1]][1]
        #print(loc, crt, crt+time_bin*SECS_IN_MINUTE - 1, colors_dict[loc])
        plt.plot([s,e - 1], [0,0], '-',linewidth=50, color=colors_dict[crt])
        crt = crt + 1

    #plt.ylim(0)
    #plt.title("Locations from "+loc_type+" data. Plot over (days): "+str(days_to_consider)+" User: "+username)
    #plt.xlabel("Locations in time", fontsize=10)
    
    no_of_ticks = (end_time - start_time)/(plot_time_interval*SEC_IN_MINUTE) + 1
    #print(plot_time_interval,no_of_ticks)
    ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, plot_time_interval)#(dates_epoch, no_of_ticks)
    
    plt.xticks(ticks, labels_utc, rotation = 90)
    plt.yticks([2], [""])
    fig.tight_layout()    
    fig.savefig(file_path)
#     if loc_type == "hmm":
#         fig.savefig("../../plots/"+username+"/"+"hmm_locations_("+str(locations_count)+")_"+str(days_to_consider)+"days_plot.png")
#     elif loc_type == "kmeans":
#         fig.savefig("../../plots/"+username+"/"+"kmeans_locations_("+str(locations_count)+")_"+str(days_to_consider)+"days_plot.png")
    
start_day = 0
days_to_consider = 30
plot_interval = 60 
base = "../../plots/gps/"
user_list = [6,72]

stops_for_users = []
unique = []
wifi_stops = []
wifi_unique = []
for user in user_list:
    username="user_"+str(user)+"_sorted"
    #file_path = base+username+"_locations_"+str(start_day)+"_"+str(days_to_consider)
    data = retrieve_data_from_user(username, start_day, days_to_consider)
    start_time = data[0][1]
    end_time = start_time + days_to_consider * DAY_INTERVAL_SECS
    
    stops = getstops_dbscan(username, data)
    no_stops = len(stops)
    stops_for_users.append(no_stops)
    if len(stops) not in unique:
        unique.append(no_stops)
    print(len(stops))
    
    # wifi loc
    total = 0
    for i in range(0,30):
        file_with_loc = "../../plots/"+username+"/day_"+str(i)+"_count_1_transitions.p"
        locations = location_data_handler.load_pickled_file(file_with_loc)
        no_wifi_stops = max(locations)
        total = total + no_wifi_stops + 1
    wifi_stops.append(total-1)
    if total not in wifi_unique:
        wifi_unique.append(no_wifi_stops)
    

fig = plt.figure()
fig.clear()
fig.set_size_inches(15,5)  
#plt.title("Gaussian Histogram")
plt.xlabel("Locations", fontsize=18)
plt.ylabel("Users", fontsize=18)    

plt.hist(stops_for_users, len(unique), alpha=0.5)
print(len(unique))
fig.tight_layout()     
fig.savefig("../../plots/random/distribution_loc_gps.png")


fig = plt.figure()
fig.clear()
fig.set_size_inches(15,5)  
#plt.title("Gaussian Histogram")
plt.xlabel("Locations", fontsize=18)
plt.ylabel("Users", fontsize=18)    

plt.hist(wifi_stops, len(wifi_unique), alpha=0.5)
print(len(wifi_unique))
fig.tight_layout()     
fig.savefig("../../plots/random/distribution_loc_wifi.png")    

suma = 0
for x in stops_for_users:
    suma = suma + x
print(suma/(0.0+len(stops_for_users)))

suma = 0
for x in wifi_stops:
    suma = suma + x
print(suma/(0.0+len(wifi_stops)))

    #colors_dict = user_data_handler.generate_color_codes_for_gps_loc(stops)
    #plot_stop_locations(stops, data, start_time, end_time, colors_dict, plot_interval*days_to_consider, file_path)
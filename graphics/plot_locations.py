'''
Created on Mar 24, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from graphics import locations_with_hmm
from graphics import locations_with_networks 
from graphics import bssids_without_rssi_strength_plot
from handlers import user_data_handler, location_data_handler
from handlers import location_data_handler
import pickle
from matplotlib.backends.backend_pdf import PdfPages
from sklearn import hmm
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import datetime
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
def plot_locations_from_hmm(list_locations_over_time_bins,locations_count, days_to_consider, time_bin, username,colors_dict, start_time, end_time, plot_time_interval):
    print(len(list_locations_over_time_bins))
    
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(25,5)       
     
    plt.xlim(start_time,end_time)
    crt = start_time
    print(list_locations_over_time_bins)
    list_locations_over_time_bins = np.array(list_locations_over_time_bins).tolist()
    print(list_locations_over_time_bins)
    for loc in list_locations_over_time_bins:
        print(loc, crt, crt+time_bin*SECS_IN_MINUTE - 1, colors_dict[loc])
        plt.plot([crt,crt+time_bin*SECS_IN_MINUTE - 10], [0,0], '-',linewidth=50, color=colors_dict[loc])
        crt = crt+time_bin*SECS_IN_MINUTE

    #plt.ylim(0)
    plt.title("Locations from HMM data. Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("Locations in time", fontsize=10)
    
    no_of_ticks = (end_time - start_time)/(plot_time_interval*SECS_IN_MINUTE) + 1
    #print(plot_time_interval,no_of_ticks)
    ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, plot_time_interval)#(dates_epoch, no_of_ticks)
    
    #print(ticks)
    #print(labels_utc)
    plt.xticks(ticks, labels_utc, rotation = 90)
    plt.yticks([2], [""])
#     plt.show()
    
    fig.savefig("../../plots/"+username+"/"+username+"_"+str(days_to_consider)+"days_hmm_locations_("+str(locations_count)+")_plot.png")
    return fig    

def plot_locations_from_network(list_locations):
    print(len(list_locations))
        

########## Needed final variables #################
base = "../../plots/"
pickled_presence_matrix_base="pickled_matrix_all_"
treshold = 0.5
###################################################

def load_pickled_file(filename):
    pickled_data = pickle.load(open(filename, "rb" ))
    #print(pickled_data)
    return pickled_data
    
def generate_files_with_presence_matrixes(user_list, start_day, days_to_consider, most_common, time_bin, plot_time_interval):
    fig_bssid_presence = dict() # user1:fig_u1, user2:fig_u2...
    for user in user_list:
        username = "user_"+str(user)+"_sorted"
        print("[User "+str(user)+"] Generating presence matrix")
        fig_bssid_presence[user] = bssids_without_rssi_strength_plot.bssid_without_rssi_strength_plot(username, start_day, days_to_consider, most_common, time_bin, plot_time_interval)
    return fig_bssid_presence

def generate_locations_based_on_networks(user_list, days_to_consider):
    components_count = dict() # user:x_locations, ...
    for user in user_list:
        print("[User "+str(user)+"] Generating connected components with Networks")
        username = "user_"+str(user)+"_sorted"        

        #Files
        gephi_file = base+username+"/"+"gephi_"+username+"_"+str(days_to_consider)+"days.gexf"
        connected_components_file = base+username+"/"+"list_connected_"+username+"_"+str(days_to_consider)+"days.txt"
        matrix_file = base+username+"/"+pickled_presence_matrix_base+username+"_"+str(days_to_consider)+"days.p"

        presence_matrix = locations_with_networks.load_pickled_matrix(matrix_file)
        G, correlated_appearance_count = locations_with_networks.create_correlation_graph(presence_matrix)
        correlated_appearance_count = locations_with_networks.normalize_correlated_appearances(presence_matrix, correlated_appearance_count)
        G,new_correlated_appearance_count = locations_with_networks.remove_week_correlations(G, correlated_appearance_count, treshold)
        
        # create gephi file
        nx.write_gexf(G,gephi_file)
        
        # count connected components
        no_connected_comp = len(nx.strongly_connected_components(G))
        components_count[user] =no_connected_comp
        print("Number of connected components: "+str(no_connected_comp))
        
        # save components
        pickle.dump(nx.strongly_connected_components(G), open(connected_components_file, "wb"))
    return components_count

def generate_locations_based_on_hmm(user_list, components_count, days_to_consider):
    location_transitions = dict() #user:Z,..
    for user in user_list:
        print("[User "+str(user)+"] Generating locations succession with HMM")
        username = "user_"+str(user)+"_sorted"    
    
        #Files
        matrix_file = base+username+"/"+pickled_presence_matrix_base+username+"_"+str(days_to_consider)+"days.p"
        transition_file = base+username+"/"+"transitions_"+username+"_"+str(components_count[user])+"loc_"+str(days_to_consider)+"days.p"
        presence_matrix = locations_with_hmm.load_pickled_matrix(matrix_file)
    
        ##### HMM
        matrix_with_bssids_on_columns, bssids_order = locations_with_hmm.create_matrix_for_hmm(presence_matrix)
        print("No bssids: ",len(bssids_order))
        print("No time bins: ",len(matrix_with_bssids_on_columns))
        print("No hidden states to identify: ",components_count[user])
        model = hmm.GaussianHMM(components_count[user])
        #print(matrix_with_bssids_on_columns)
        X = np.array(matrix_with_bssids_on_columns)
        model.fit([X])
        Z = model.predict(X)
        location_transitions[user]=Z
        #write to file
        pickle.dump(Z, open(transition_file, "wb"))
    return location_transitions

######## Values initialization ########
# for the plot without rssi
start_day = 0
most_common = -1
time_bin = 5
plot_interval = 60
days_to_consider = 2
user_list = [6]
print(user_list)
########################################
#presence_figures = generate_files_with_presence_matrixes(user_list, start_day, days_to_consider, most_common, time_bin, days_to_consider*plot_interval)
#connected_components_count = generate_locations_based_on_networks(user_list, days_to_consider)
connected_components_count =dict()
#connected_components_count[1]=19
connected_components_count[6]=19
#location_transitions = generate_locations_based_on_hmm(user_list, connected_components_count, days_to_consider)

# get locations from results of networks
# get locations from results of hmm
#connected_components_count =dict()
#connected_components_count[1] = 32
#connected_components_count[6] = 35
figures_locations = dict()
for user in user_list:
    username = "user_"+str(user)+"_sorted"
    #filename = base+username+"/"+"transitions_"+username+"_"+str(19)+"loc_"+str(days_to_consider)+"days.p"
    filename = base+username+"/"+"pickled_matrix_all_"+username+"_"+str(days_to_consider)+"days.p"
    pickled_transitions = load_pickled_file(filename)
    hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(pickled_transitions)
    print("Created matrix and moving on to generating transitions")
    pickled_transitions = location_data_handler.state_transitions(hmm_matrix, connected_components_count[user])
    print(pickled_transitions)
   
    locations = []
    for i in range(0,connected_components_count[user]):
        locations.append(i)
    colors_dict = user_data_handler.generate_color_codes_for_bssid(locations)
    print(colors_dict)
    
    user_data = user_data_handler.retrieve_data_from_user(username,start_day,days_to_consider)
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]    
    print("Plot HMM locations")
    figures_locations[user] = plot_locations_from_hmm(pickled_transitions,connected_components_count[user], days_to_consider,time_bin, username,colors_dict,start_time, end_time, days_to_consider*plot_interval)

"""for user in user_list:
    username = "user_"+str(user)+"_sorted"
    pp = PdfPages(base+username+"/"+"bssids_and_locations_("+str(connected_components_count[user])+")"+username+"_for_"+str(days_to_consider)+".pdf")
    pp.savefig(presence_figures[user])
    pp.savefig(figures_locations[user])
    pp.close()"""
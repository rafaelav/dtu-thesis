'''
Created on Mar 24, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from graphics import locations_with_hmm
from graphics import locations_with_networks 
from graphics import bssids_without_rssi_strength_plot
import pickle
from sklearn import hmm
import numpy as np
import networkx as nx

def plot_locations_from_hmm(list_locations_over_time_bins):
    print(len(list_locations_over_time_bins))
def plot_locations_from_network(list_locations):
    print(len(list_locations))
    
######## Values initialization ########
# for the plot without rssi
start_day = 0
most_common = -1
time_bin = 5
plot_interval = 60
# plot without rssi, networks, hmm
days_to_consider = 1
# for networks and hmm
base = "../../plots/"
pickled_presence_matrix_base="pickled_matrix_all_"
# for networks
treshold = 0.5

user_list = [1,6]
########################################
    
# for each user
print(user_list)

for i in user_list:
    print("For user "+str(i))
    username = "user_"+str(i)+"_sorted"

    ##### Plot for presence of bssids
    print("#Moving to determining presence of bssids over time ...")
    fig_bssid_presence = bssids_without_rssi_strength_plot.bssid_without_rssi_strength_plot(username, start_day, days_to_consider, most_common, time_bin, days_to_consider*plot_interval)
    print("finished presence matrix")
    
for i in user_list:
    print("For user "+str(i))
    username = "user_"+str(i)+"_sorted"        
    ##### Networks
    print("#Moving to Network work ...")
    gephi_file = base+username+"/"+"gephi_"+username+"_"+str(days_to_consider)+"days.gexf"
    connected_components_file = base+username+"/"+"list_connected_"+username+"_"+str(days_to_consider)+"days.txt"
    #clique_components_file = base+username+"/"+"list_cliques_"+username+"_"+str(days_to_consider)+"days.txt"
    # load the presence matrix for signals for all bssid in 5 min time bins
    matrix_file = base+username+"/"+pickled_presence_matrix_base+username+"_"+str(days_to_consider)+"days.p"
    presence_matrix = locations_with_networks.load_pickled_matrix(matrix_file)
    G, correlated_appearance_count = locations_with_networks.create_correlation_graph(presence_matrix)
    correlated_appearance_count = locations_with_networks.normalize_correlated_appearances(presence_matrix, correlated_appearance_count)
    G,new_correlated_appearance_count = locations_with_networks.remove_week_correlations(G, correlated_appearance_count, treshold)
    nx.write_gexf(G,gephi_file)
    no_connected_comp = len(nx.strongly_connected_components(G)) # used also in HMM
    print("Number of connected comp: "+str(no_connected_comp))
    pickle.dump(nx.strongly_connected_components(G), open(connected_components_file, "wb"))
    #print("Number of clique comp: "+str(len(list(nx.find_cliques(G)))))
    #pickle.dump(list(nx.find_cliques(G)), open(clique_components_file, "wb"))
    ##### Plotting for Networks
    list_locations = pickle.load( open( connected_components_file, "rb" ) )
    plot_locations_from_network(list_locations)    
    
for i in user_list:
    print("For user "+str(i))
    username = "user_"+str(i)+"_sorted"    

    # load the presence matrix for signals for all bssid in 5 min time bins
    matrix_file = base+username+"/"+pickled_presence_matrix_base+username+"_"+str(days_to_consider)+"days.p"
    presence_matrix = locations_with_hmm.load_pickled_matrix(matrix_file)

    ##### HMM
    print("#Moving to HMM work ...")
    fig_filename = base+username+"/"+"locations_graph_"+str(days_to_consider)+"days.pdf"
    matrix_with_bssids_on_columns, bssids_order = locations_with_hmm.create_matrix_for_hmm(presence_matrix)
    print("No bssids: ",len(bssids_order))
    print("No time bins: ",len(matrix_with_bssids_on_columns))
    print("No hidden states to identify: ",no_connected_comp)
    model2 = hmm.GaussianHMM(no_connected_comp)
    #print(matrix_with_bssids_on_columns)
    X = np.array(matrix_with_bssids_on_columns)
    model2.fit([X])
    Z2 = model2.predict(X)
    
    ##### PLotting for HMM
    plot_locations_from_hmm(Z2)
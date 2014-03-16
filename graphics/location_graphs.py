'''
Created on Mar 15, 2014

@author: rafa
'''
import pickle
import networkx as nx

def load_pickled_matrix(filename):
    pickled_data = pickle.load(open(filename, "rb" ))
    #print(pickled_data)
    return pickled_data

def get_presence_in_all_time_bins_all_nodes(presence_matrix):
    presence_count = dict()
    for bssid in presence_matrix.keys():
        count = 0
        for elem in presence_matrix[bssid]:
            if elem == 1:
                count = count + 1
        presence_count[bssid] = count
    #print(presence_count)
    return presence_count

def normalize_correlated_appearances(presence_matrix, correlated_appearance_count):
    presence_count = get_presence_in_all_time_bins_all_nodes(presence_matrix)
    for (u,v) in correlated_appearance_count.keys():
        presence_u = presence_count[u]
        presence_v = presence_count[v]
        # normalizing by dividing to the maximum number of possible times they could have appeared together
        correlated_appearance_count[(u,v)] = correlated_appearance_count[(u,v)]/(max(presence_u,presence_v)+0.0)
    print(correlated_appearance_count)
    return correlated_appearance_count 

def remove_week_correlations(G, correlated_appearance_count, treshold):
    for (u,v) in correlated_appearance_count.keys():
        if correlated_appearance_count[(u,v)] < treshold:
            # remove edge and correlation_appearance_count key
            G.delete_edge(u,v)
            #TODO key rem
            
#def identify_strongly_conex_components(G):

def create_correlation_graph(presence_matrix):
    """ Creates a graph that says which bssids are present at the same time and how often"""
    bssids = presence_matrix.keys()
    G = nx.Graph()
    # add all nodes (bssid labels)
    G.add_nodes_from(bssids)
    # count the number of times when 2 nodes have appeared at the same time (for each nodes)
    correlated_appearance_count = dict() # {(node1, node2): no_of_times_they_appeared_in_same_time_bin)..}
    #print(G.nodes())
    
    for bssid in presence_matrix.keys():
        # get the number of time bins we are calculating the graph for
        number_of_time_bins = len(presence_matrix[bssid]) 
        break

    for i in range(0,number_of_time_bins):
        # get what bssid are present in current time bin
        present_bssid_in_ith_time_bin = []
        for bssid in bssids:
            if presence_matrix[bssid][i] == 1:
                present_bssid_in_ith_time_bin.append(bssid)
        # if there are not edges between bssids, craete them; if there are increase the number of appearances
        for u in range(0,len(present_bssid_in_ith_time_bin)):
            for v in range(u+1,len(present_bssid_in_ith_time_bin)):
                node_u = present_bssid_in_ith_time_bin[u]
                node_v = present_bssid_in_ith_time_bin[v]
                if G.has_edge(node_u, node_v):
                    correlated_appearance_count[(node_u,node_v)] = correlated_appearance_count[(node_u,node_v)] + 1
                else:
                    G.add_edge(node_u, node_v)
                    correlated_appearance_count[(node_u,node_v)] = 1
    return G, correlated_appearance_count                 
    
    
base = "../../plots/"
days_to_consider = 2
for i in range (6,7):
    username = "user_"+str(i)+"_sorted"
    # load the presence matrix for signals for all bssid in 5 min time bins
    presence_matrix = load_pickled_matrix(base+username+"/"+"pickled_matrix_"+username+"_"+str(days_to_consider)+"days.p")
    G, correlated_appearance_count = create_correlation_graph(presence_matrix)
    normalize_correlated_appearances(presence_matrix, correlated_appearance_count)
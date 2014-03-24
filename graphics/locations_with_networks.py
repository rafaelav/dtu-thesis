'''
Created on Mar 15, 2014

@author: rafa
'''
import pickle
import networkx as nx
import matplotlib.pyplot as plt

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
    #print(correlated_appearance_count)
    return correlated_appearance_count 

def remove_week_correlations(G, correlated_appearance_count, treshold):
    to_remove_list = []
    for (u,v) in correlated_appearance_count.keys():
        if correlated_appearance_count[(u,v)] < treshold:
            # remove edge and correlation_appearance_count key
            G.remove_edge(u,v)
            to_remove_list.append((u,v))

    new_correlation_appearacne_count = dict()
    
    for (u,v) in correlated_appearance_count.keys():
        if (u,v) not in to_remove_list:
            new_correlation_appearacne_count[(u,v)] = correlated_appearance_count[(u,v)]
            
    return G,new_correlation_appearacne_count        

#def identify_strongly_conex_components(G):

def create_correlation_graph(presence_matrix):
    """ Creates a graph that says which bssids are present at the same time and how often"""
    bssids = presence_matrix.keys()
    G = nx.Graph()
    # add all nodes (bssid labels)
    print("Bssids in graph: ",len(bssids))
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
    

def draw_graph(G, filename, labels=None, graph_layout='shell',
               node_size=150, node_color='blue', node_alpha=0.3,
               node_text_size=6,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):

    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)

    # draw graph
    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size, 
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                            font_family=text_font)

    # show graph
    plt.axis('off')
    plt.savefig(filename)
    
"""base = "../../plots/"
days_to_consider = 2
treshold = 0.5

for i in range (1,2):
    username = "user_"+str(i)+"_sorted"
    fig_filename = base+username+"/"+"locations_graph_"+str(days_to_consider)+"days.pdf"
    matrix_file = base+username+"/"+"pickled_matrix_"+username+"_"+str(days_to_consider)+"days.p"
    gephi_file = base+username+"/"+"gephi_"+username+"_"+str(days_to_consider)+"days.gexf"
    connected_components_file = base+username+"/"+"list_connected_"+username+"_"+str(days_to_consider)+"days.txt"
    clique_components_file = base+username+"/"+"list_cliques_"+username+"_"+str(days_to_consider)+"days.txt"
    # load the presence matrix for signals for all bssid in 5 min time bins
    presence_matrix = load_pickled_matrix(matrix_file)
    G, correlated_appearance_count = create_correlation_graph(presence_matrix)
    correlated_appearance_count = normalize_correlated_appearances(presence_matrix, correlated_appearance_count)
    G,new_correlated_appearance_count = remove_week_correlations(G, correlated_appearance_count, treshold)
    #save_graph(G,base+username+"/"+"locations_graph_"+str(days_to_consider)+"days.pdf")
    #draw_graph(G, fig_filename, graph_layout='random')
    nx.write_gexf(G,gephi_file)
    print("Number of connected comp: "+str(len(nx.strongly_connected_components(G))))
    pickle.dump(nx.strongly_connected_components(G), open(connected_components_file, "wb"))
    print("Number of clique comp: "+str(len(list(nx.find_cliques(G)))))
    pickle.dump(list(nx.find_cliques(G)), open(clique_components_file, "wb"))"""
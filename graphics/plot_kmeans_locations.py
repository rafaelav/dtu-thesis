'''
Created on May 6, 2014

@author: rafa
'''

import sys
sys.path.append( ".." )
from handlers import user_data_handler
from handlers import location_data_handler
import pickle
import os.path
from sklearn.cluster import KMeans

# using K-fold cross validation is used
K = 10
# final variable
base = "../../plots/"
LOC_TYPE = "kmeans"
init='k-means++'
n_init=10
max_iter=500
tol=0.0001
precompute_distances=True
verbose=0
random_state=None
copy_x=True
n_jobs=1

def start_plot_hmm_locations (user_list, start_day, days_to_consider, m_most_popular_bssids, time_bin, plot_interval):
    for user in user_list:
        user_file = "user_"+str(user)+"_sorted"
        determine_estimated_locations_and_plot(user_file,start_day,days_to_consider,m_most_popular_bssids,time_bin,plot_interval)    
# # list of users
# users_list = [6]
# # set values 
# start_day = 0 
# days_to_consider = 1
# m_most_popular_bssids = -1
# time_bin = 5
# plot_interval = 60
DAY_INTERVAL_SECS = 24 * 60 * 60
def determine_estimated_locations_and_plot(user_file,start_day,days_to_consider,m_most_popular_bssids,time_bin,plot_interval):
    pickled_matrix_file = base+user_file+"/"+"pickled_matrix_all_"+user_file+"_"+str(days_to_consider)+"days.p"
    
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)    
    start_time = user_data[0][1]
    end_time = end_time = start_time + days_to_consider * DAY_INTERVAL_SECS
    
    # only re-calculate presence matrxi and pickle it if it doens't already exist
    if not os.path.isfile(pickled_matrix_file):
        print("Matrix was not claculated previously... need to do this now")
        # make presence matrix
        location_data_handler.pickle_presence_matrix(user_file, start_day, days_to_consider, time_bin, m_most_popular_bssids)
        print("Matrix calculation is complete")
            
    # load matrix and number of estimated locations
    presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)
    
    # make presence matrix for hmm
    hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(presence_matrix)
    
    # determine locations estimation
    estimated_hidden_states, transitions_between_states = location_data_handler.estimate_locations_k_fold_cross_validation(K, hmm_matrix, 2, 10, LOC_TYPE)
    print("Results (estimated number of locations and transitions between them")
    print(estimated_hidden_states)
    estimated_locations_file = base+user_file+"/"+"estimated_locations_kmeans_"+user_file+"_"+str(days_to_consider)+"days.p"
    print(transitions_between_states)
    transitions_file = base+user_file+"/"+"transitions_"+user_file+"_"+str(estimated_hidden_states)+"loc_"+str(days_to_consider)+"days.p"
    
    # save transitions and save number of estimated states
    pickle.dump(transitions_between_states, open(transitions_file, "wb"))
    pickle.dump(estimated_hidden_states, open(estimated_locations_file, "wb"))
    
    # get colors for the locations (0 to estimated_hidden_states)
    locations = []
    for i in range(0,estimated_hidden_states):
        locations.append(i)
    colors_dict = user_data_handler.generate_color_codes_for_bssid(locations)
        
    # file path where to plot
    file_path = "../../plots/"+user_file+"/"+"kmeans_locations_("+str(estimated_hidden_states)+")_"+str(days_to_consider)+"days_plot.png"
    # plot transitions
    location_data_handler.plot_locations(transitions_between_states, days_to_consider, time_bin, user_file, colors_dict, start_time, end_time, plot_interval*days_to_consider, LOC_TYPE,file_path)

# for user in users_list:
#     user_file = "user_"+str(user)+"_sorted"
#     determine_estimated_locations_and_plot(user_file,start_day,days_to_consider,m_most_popular_bssids,time_bin,plot_interval)
'''
Created on Apr 5, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
from handlers import location_data_handler

# using K-fold cross validation is used
K = 10

# set values
username = "user_1_sorted" 
start_day = 0 
days_to_consider = 1
m_most_popular_bssids = -1
time_bin = 5
base = "../../plots/"
pickled_matrix_file = base+username+"/"+"pickled_matrix_all_"+username+"_"+str(days_to_consider)+"days.p"

# make presence matrix
location_data_handler.pickle_presence_matrix(username, start_day, days_to_consider, time_bin, m_most_popular_bssids)

# load matrix
presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)

# make presence matrix for hmm
hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(presence_matrix)

hmm_matrix = [[1,1,1,0,0,0],
[1,1,1,0,0,0],
[1,1,0,0,0,0],
[0,0,0,1,1,1],
[0,0,0,1,1,0],
[0,0,0,1,1,1],
[0,0,1,1,1,0],
[0,0,1,1,1,0]]
K=4
# determine locations estimation
estimated_hidden_states = location_data_handler.estimate_locations_k_fold_cross_validation(K, hmm_matrix, 2, 4)
print(estimated_hidden_states)
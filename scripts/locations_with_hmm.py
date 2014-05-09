'''
Created on Apr 5, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
from handlers import location_data_handler
import pickle

# using K-fold cross validation is used
K = 10

# set values
user_file = "user_6_sorted" 
start_day = 0 
days_to_consider = 2
m_most_popular_bssids = -1
time_bin = 5
plot_interval = 60
base = "../../plots/"
pickled_matrix_file = base+user_file+"/"+"pickled_matrix_all_"+user_file+"_"+str(days_to_consider)+"days.p"

user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)    
start_time = user_data[0][1]
end_time = user_data[len(user_data)-1][1]

# make presence matrix
location_data_handler.pickle_presence_matrix(user_file, start_day, days_to_consider, time_bin, m_most_popular_bssids)

# load matrix
presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)

# make presence matrix for hmm
hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(presence_matrix)

"""hmm_matrix = [[1,1,1,0,0,0],
[1,1,1,0,0,0],
[1,1,0,0,0,0],
[0,0,0,1,1,1],
[0,0,0,1,1,0],
[0,0,0,1,1,1],
[0,0,1,1,1,0],
[0,0,1,1,1,0]]
K=4"""
# determine locations estimation
estimated_hidden_states, transitions_between_states = location_data_handler.estimate_locations_k_fold_cross_validation(K, hmm_matrix, 2, 10)
print("Results (estimated number of locations and transitions between them")
print(estimated_hidden_states)
print(transitions_between_states)
transitions_file = base+user_file+"/"+"transitions_"+user_file+"_"+str(estimated_hidden_states)+"loc_"+str(days_to_consider)+"days.p"

# save transitions
pickle.dump(transitions_between_states, open(transitions_file, "wb"))

# get colors for the locations (0 to estimated_hidden_states)
locations = []
for i in range(0,estimated_hidden_states):
    locations.append(i)
colors_dict = user_data_handler.generate_color_codes_for_bssid(locations)
    
# plot transitions
location_data_handler.plot_locations(transitions_between_states, days_to_consider, time_bin, user_file, colors_dict, start_time, end_time, plot_interval*days_to_consider, "hmm")
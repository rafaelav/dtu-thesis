'''
Created on May 18, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
from handlers import location_data_handler
import pickle
import os.path

# using K-fold cross validation is used
K = 10
# final variable
base = "../../plots/"
LOC_TYPE = "hmm"

def calculate_transitions_over_time(user_file, start_day, days_count, m_most_popular_bssids, time_bin, iterations):
    days_to_consider = 1 # always process one day at the time
    for day in range(start_day, start_day+days_count):
        # create the transition matrix for each day
        transitions = create_day_transition_array(user_file, day, days_to_consider, m_most_popular_bssids, time_bin, iterations)
        save_transitions(user_file, day, transitions)
        
def save_transitions(user_file, day, transitions):
    transitions_file = base+user_file+"/"+"day_"+str(day)+"_transitions.p"
    
    # save transitions for currentd day
    pickle.dump(transitions, open(transitions_file, "wb"))    
        
def create_day_transition_array(user_file, day, days_to_consider, m_most_popular_bssids,time_bin, iterations):
    pickled_matrix_file = base+user_file+"/"+"day_"+str(day)+"_pickled_presence_matrix.p"

    # only re-calculate presence matrxi and pickle it if it doens't already exist
    if not os.path.isfile(pickled_matrix_file):
        print("Matrix was not claculated previously... need to do this now")
        # make presence matrix
        pickle_presence_matrix(user_file, day, days_to_consider, time_bin, m_most_popular_bssids)
        print("Matrix calculation is complete")
    
    # load matrix
    presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)
    
    # make presence matrix for hmm
    hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(presence_matrix)
    
    # determine locations estimation
    dict_estimations = dict()
    for iter in range(0,iterations):
        print("ITERRATION: "+str(iter+1)+"/"+str(iterations))
        estimated_hidden_states, transitions_between_states = location_data_handler.estimate_locations_k_fold_cross_validation(K, hmm_matrix, 2, 10, LOC_TYPE)
        if estimated_hidden_states not in dict_estimations.keys(): # this number was never estimated before
            dict_estimations[estimated_hidden_states] = []
        dict_estimations[estimated_hidden_states].append(transitions_between_states) # add solution for this estimations
    
    # find most likely estimate and pick a transition
    max = 0
    states = 0
    for key in dict_estimations.keys():
        if len(dict_estimations[key])>max:
            max = len(dict_estimations[key])
            states = key
    
    estimated_hidden_states = states # get the best posibility
    transitions_between_states = dict_estimations[estimated_hidden_states][0] # take fist transitions it estimated for given states 

    print("DAY "+str(day)+" - Results (estimated number of locations and transitions between them")
    print(estimated_hidden_states)
    print(transitions_between_states)
    return transitions_between_states

def pickle_presence_matrix(user_file, start_day, days_to_consider, time_bin, m_most_popular_bssids):
    ### Prepare and calculate pickled matrix for m_most_popolar
    # prepare needed data
    user_data, start_time, end_time, bssid_times_and_rssis_dict = location_data_handler.prepare_data(user_file, start_day, days_to_consider, m_most_popular_bssids)
    # get matrix
    presence_on_rows, column_elements =  location_data_handler.get_bssid_presence_matrix(start_time, end_time, bssid_times_and_rssis_dict, time_bin)

    print("Number of bssids in matrix:",len(presence_on_rows.keys()))
    print("Need to pickle")
    if m_most_popular_bssids == -1:
        pickle.dump(presence_on_rows, open("../../plots/"+user_file+"/"+"day_"+str(start_day)+"_pickled_presence_matrix.p", "wb"))
    else:
        print("NOT TRATING CASE WITH LESS BSSIDS")
    print("Pickled")
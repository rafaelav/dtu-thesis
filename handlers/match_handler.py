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

def calculate_transitions_over_time(user_file, start_day, days_count, step, m_most_popular_bssids, time_bin, plot_interval, iterations):
    days_to_consider = step # always process step days at the time
    start_days = []
    for day in range(start_day, start_day+days_count,step):
        start_days.append(day)
        # create the transition matrix for each day
        transitions, estimated_hidden_states, start_time, end_time = create_transition_array(user_file, day, days_to_consider, m_most_popular_bssids, time_bin, iterations)
        save_transitions(user_file, day, days_to_consider, transitions)
        file_path = "../../plots/"+user_file+"/"+"hmm_locations_"+"day_"+str(day)+"_count_"+str(days_to_consider)+"_plot.png"
        plot_transitions(user_file, days_to_consider, estimated_hidden_states, transitions, time_bin, start_time, end_time, plot_interval, file_path)
    print(start_days)
        
def save_transitions(user_file, day, days_to_consider, transitions):
    transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(days_to_consider)+"_transitions.p"
    
    # save transitions for currentd day
    pickle.dump(transitions, open(transitions_file, "wb"))    
        
def create_transition_array(user_file, day, days_to_consider, m_most_popular_bssids,time_bin, iterations):
    pickled_matrix_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(days_to_consider)+"_pickled_presence_matrix.p"

    user_data = user_data_handler.retrieve_data_from_user(user_file,day,days_to_consider)    
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]
    
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

    print("DAY "+str(day)+" COUNT "+str(days_to_consider)+" - Results (estimated number of locations and transitions between them")
    print(estimated_hidden_states)
    print(transitions_between_states)
    return transitions_between_states, estimated_hidden_states, start_time, end_time

def plot_transitions(user_file, days_to_consider, estimated_hidden_states, transitions, time_bin, start_time, end_time, plot_interval, file_path):
    # get colors for the locations (0 to estimated_hidden_states)
    locations = []
    for i in range(0,estimated_hidden_states):
        locations.append(i)
    colors_dict = user_data_handler.generate_color_codes_for_bssid(locations)
        
    # plot transitions
    location_data_handler.plot_locations(transitions, days_to_consider, time_bin, user_file, colors_dict, start_time, end_time, plot_interval*days_to_consider, LOC_TYPE, file_path)


def pickle_presence_matrix(user_file, start_day, days_to_consider, time_bin, m_most_popular_bssids):
    ### Prepare and calculate pickled matrix for m_most_popolar
    # prepare needed data
    user_data, start_time, end_time, bssid_times_and_rssis_dict = location_data_handler.prepare_data(user_file, start_day, days_to_consider, m_most_popular_bssids)
    # get matrix
    presence_on_rows, column_elements =  location_data_handler.get_bssid_presence_matrix(start_time, end_time, bssid_times_and_rssis_dict, time_bin)

    print("Number of bssids in matrix:",len(presence_on_rows.keys()))
    print("Need to pickle")
    if m_most_popular_bssids == -1:
        pickle.dump(presence_on_rows, open("../../plots/"+user_file+"/"+"day_"+str(start_day)+"_count_"+str(days_to_consider)+"_pickled_presence_matrix.p", "wb"))
    else:
        print("NOT TRATING CASE WITH LESS BSSIDS")
    print("Pickled")
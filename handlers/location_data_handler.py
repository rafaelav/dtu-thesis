'''
Created on Apr 5, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler

import pickle
import math
from sklearn import hmm
import numpy as np

SECS_IN_MINUTE = 60

def get_start_of_time_bins(start_time,end_time,time_bin):
    """Receives a time interval [start_time, end_time]. Divides the interval in seg oftime_bin len 
    starting from first time stamp (start_time). Returns list with starting moments of time bins"""
    start_moments_list = []
    start_moments_list.append(start_time)
    
    while start_time+time_bin*SECS_IN_MINUTE < end_time:
        start_time = start_time + time_bin*SECS_IN_MINUTE
        start_moments_list.append(start_time)
    
    return start_moments_list 
        
def get_bssid_presence_matrix(start_time, end_time, bssid_dict, time_bin):   
    """Parameters: start_time, end_time and time_bin (length) used in dividing the time into bins for
    which we will say if a bssid has been spotted in that bin or not; bssid_dict[bssid] = [(time,rssi)...]
    contains for each bssid a list with the timestamps at which that bssid is seen and the rssi value for 
    that apparence.
    Returns: presence_on_rows[bssid] = [0 1 1 ...] - list for each bssid with 1 or 0 for each time bin 
    (0 if they are not seen during that time bin, 1 if yes); column_elements is a list with the start times
    for the time bins.""" 
    column_elements = get_start_of_time_bins(start_time,end_time,time_bin)
     
    presence_on_rows = dict()
    
    for bssid in bssid_dict.keys():
        presence_on_rows[bssid] = []
        
    for bssid in bssid_dict.keys():    
        bssid_apparition_time_rssi_values = bssid_dict[bssid] # [(time,rssi)....]
        bssid_apparition_time_rssi_values = sorted(bssid_apparition_time_rssi_values, key=lambda x: x[0])
        bssid_apparition_time_list = []
        # getting only times
        for element in bssid_apparition_time_rssi_values:
            bssid_apparition_time_list.append(element[0])
        
        bssid_apparition_time_list = sorted(bssid_apparition_time_list, key=lambda x: x)
        # mark for each column element
        for col_elem in column_elements:
            found = False
            for elem in bssid_apparition_time_list:
                # it appears in time bin
                if elem >= col_elem and elem < col_elem+time_bin*SECS_IN_MINUTE:
                    found = True
                    break
                # already skipped for time bin (so it for sure is not there)
                elif elem >= col_elem+time_bin*SECS_IN_MINUTE:
                    break
            if found == True:
                presence_on_rows[bssid].append(1)
            else:
                presence_on_rows[bssid].append(0)

    #print(presence_on_rows)
    return presence_on_rows, column_elements

def prepare_data(user_file, start_day, days_to_consider, m_most_popular_bssids):
    """User file: user_file; From which day to start retrieving data: start_day; For how many days: days_to_consider
    How many bssids (based on their popularity) to take into consideration: m_most_popular_bssids (auto to all)
    Returns start and end time of user data and the dictionary with bssids and their apparition times 
    bssid:[(time,rssid),...]""" 
    # get data from file
    user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)    
    start_time = user_data[0][1]
    end_time = user_data[len(user_data)-1][1]
    
    most_common_bssids = user_data_handler.get_most_common_bssids(user_data, m_most_popular_bssids)
    bssid_times_and_rssis = user_data_handler.get_bssid_info_from_data(user_data, most_common_bssids)
    
    print("Bssids considered = "+str(len(bssid_times_and_rssis.keys())))  
    return user_data, start_time, end_time, bssid_times_and_rssis

def pickle_presence_matrix(user_file, start_day, days_to_consider, time_bin, m_most_popular_bssids):
    ### Prepare and calculate pickled matrix for m_most_popolar
    # prepare needed data
    user_data, start_time, end_time, bssid_times_and_rssis_dict = prepare_data(user_file, start_day, days_to_consider, m_most_popular_bssids)
    # get matrix
    presence_on_rows, column_elements =  get_bssid_presence_matrix(start_time, end_time, bssid_times_and_rssis_dict, time_bin)

    print("Number of bssids in matrix:",len(presence_on_rows.keys()))
    print("Need to pickle")
    if m_most_popular_bssids == -1:
        pickle.dump(presence_on_rows, open("../../plots/"+user_file+"/"+"pickled_matrix_all_"+user_file+"_"+str(days_to_consider)+"days.p", "wb"))
    else:
        pickle.dump(presence_on_rows, open("../../plots/"+user_file+"/"+"pickled_matrix_best"+str(m_most_popular_bssids)+"_"+user_file+"_"+str(days_to_consider)+"days.p", "wb"))
    print("Pickled")
    
def load_pickled_file(filename):
    pickled_data = pickle.load(open(filename, "rb" ))
    return pickled_data

def create_matrix_for_hmm(presence_matrix):
    """Param: Presence matrix, Returns: transposed matrix (such that bssids are on columns not lines) and bssids"""
    result_matrix = []
    bssids = presence_matrix.keys()
    
    time_bins = len(presence_matrix[bssids[0]])
    
    for i in range(0,time_bins):
        # calculate line as (AP1, AP2,... APn) presence indicators
        line = []
        for bssid in bssids:
            # get for each bssid the list with it's presence in time bins
            presence_in_time_bins = presence_matrix[bssid]
            # get the presence in the i-th time bin
            line.append(presence_in_time_bins[i])
        if len(line)!=len(bssids):
            print("Error! Not the correct number of bssids considered for a line in presence matrix")
        result_matrix.append(line)
    
    if len(result_matrix)!=time_bins:
        print("Error! Not the correct number of lines in presence matrix")        
    # matrix and the order considered for the bssids in the matrix
    return result_matrix, bssids

def state_transitions(matrix, loc_count):
        model = hmm.GaussianHMM(loc_count, "full")
        #print(matrix_with_bssids_on_columns)
        X = np.array(matrix)
        model.fit([X])
        Z = model.predict(X)
        return Z
    
def get_similarity(test_elem, training_elem):
    if len(test_elem)!=len(training_elem):
        print("Error in length of fingerprints")
    
    value = 0.0
    for i in range(0,len(test_elem)):
        value = value + math.fabs(test_elem[i]-training_elem[i])
        
    return value

def get_accuracy(list_full_prediction, list_locations_for_full):
    different = 0
    for crt in range(0,len(list_full_prediction)):
        if list_full_prediction[crt] != list_locations_for_full[crt]:
            different = different + 1
    return different
        
def predict_locations_for_test_data(training_data, test_data, list_locations_for_training, loc_count):
    list_locations_for_test = []
    # for each test element 
    for test_elem in test_data:
        similarity_to_location = dict()
        # the predicted locations can only be from the ones existing in the training set
        for i in list_locations_for_training:
            if i not in similarity_to_location.keys():
                similarity_to_location[i] = 0.0        
        
        print(test_elem)
        print(similarity_to_location)
        crt = 0
        
        # for each element in the training set
        for training_elem in training_data:
            # calculate similarity between test element and element in training set
            sim = get_similarity(test_elem, training_elem)
            similarity_to_location[list_locations_for_training[crt]] = similarity_to_location[list_locations_for_training[crt]] + sim
            crt = crt + 1

        print(similarity_to_location)        
        probable_location_for_test_elem = list_locations_for_training[0]
        for key in similarity_to_location.keys():
            if similarity_to_location[key] < similarity_to_location[probable_location_for_test_elem]:
                probable_location_for_test_elem = key
        
        list_locations_for_test.append(probable_location_for_test_elem)
    return list_locations_for_test

def estimate_locations_k_fold_cross_validation(K, data, min_loc, max_loc):
    # Gets K folding factor and the min_locations and max_locations to consider. Returns best estimated
    # number of locations that can represent the data
    print(K)
    full_predictions_accuracy = dict() # keeps how accurate was the estimation for each considered no of locations
    for loc_count in range(min_loc, max_loc+1):
        print("Locations considered: ",loc_count)
        locations_for_full = state_transitions(data, loc_count)
        list_locations_for_full = np.array(locations_for_full).tolist()
        list_full_prediction = []
        for i in range(0,K):
            if i<K-1:
                test_data = data[i*(len(data)/K):(i+1)*(len(data)/K)]
            else:
                test_data = data[i*(len(data)/K):]

            #if i!=0:            
            training_data = data[0:i*(len(data)/K)]
            locations_for_training = list_locations_for_full[0:i*(len(data)/K)]

            if i<K-1: 
                training_data = training_data + data[(i+1)*(len(data)/K):]
                locations_for_training = locations_for_training + list_locations_for_full[(i+1)*(len(data)/K):]
            
            # convert locations for training to array, but keep a list copy
            list_locations_for_training = locations_for_training
            locations_for_training = np.asarray(locations_for_training)
            
#            print(data)
#            print(training_data)
#            print(test_data)
            #print("Data, training, test size: ",len(data),len(training_data),len(test_data))

#            print("[Locations] Training",list_locations_for_training)
            list_predicted_locations_for_test = predict_locations_for_test_data(training_data, test_data, list_locations_for_training, loc_count)
#            print("[Locations] Test",list_predicted_locations_for_test)
            list_full_prediction = list_full_prediction + list_predicted_locations_for_test
        print("[Locations] Full",list_locations_for_full)
        print("[Locations] Full prediction", list_full_prediction)
        full_predictions_accuracy[loc_count] = get_accuracy(list_full_prediction, list_locations_for_full)
    
    best_no_locations_estimated = min_loc
    for key in full_predictions_accuracy.keys():
        if full_predictions_accuracy[key] < full_predictions_accuracy[best_no_locations_estimated]:
            best_no_locations_estimated = key
    print(full_predictions_accuracy)
    return best_no_locations_estimated
"""
def estimate_locations_k_fold_cross_validation(K, data, min_loc, max_loc):
    Gets K folding factor and the min_locations and max_locations to consider. Returns best estimated
    number of locations that can represent the data
    print(K)
    full_predictions_accuracy = dict() # keeps how accurate was the estimation for each considered no of locations
    for loc_count in range(min_loc, max_loc+1):
        full_predictions_accuracy[loc_count] = 0
        print("Locations considered: ",loc_count)
#        locations_for_full = state_transitions(data, loc_count)
#        list_locations_for_full = np.array(locations_for_full).tolist()
#        list_full_prediction = []
        list_locations_for_training = []
        for i in range(0,K):
            if i<K-1:
                test_data = data[i*(len(data)/K):(i+1)*(len(data)/K)]
            else:
                test_data = data[i*(len(data)/K):]

            #if i!=0:            
            training_data = data[0:i*(len(data)/K)]

            if i<K-1: 
                training_data = training_data + data[(i+1)*(len(data)/K):]
                        
            print(data)
            print(training_data)
            print(test_data)
            #print("Data, training, test size: ",len(data),len(training_data),len(test_data))

            if len(list_locations_for_training) == 0:
                locations_for_training = state_transitions(training_data, loc_count)
                list_locations_for_training = np.array(locations_for_training).tolist()
            print("[Locations] Training",list_locations_for_training)
            
            list_predicted_locations_for_test = predict_locations_for_test_data(training_data, test_data, list_locations_for_training, loc_count)
            print("[Locations] Test (exp)",list_predicted_locations_for_test)
            
            list_locations_for_test = state_transitions(test_data, loc_count)
            print("[Locations] Test (calc)",list_locations_for_test)
            
            full_predictions_accuracy[loc_count] = full_predictions_accuracy[loc_count] + get_results_difference(list_predicted_locations_for_test, list_locations_for_test)
    
    best_no_locations_estimated = min_loc
    for key in full_predictions_accuracy.keys():
        if full_predictions_accuracy[key] < full_predictions_accuracy[best_no_locations_estimated]:
            best_no_locations_estimated = key
    print(full_predictions_accuracy)
    return best_no_locations_estimated
"""
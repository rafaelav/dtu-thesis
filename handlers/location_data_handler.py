'''
Created on Apr 5, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler

import random
import pickle
import math
from sklearn import hmm
import numpy as np
from sklearn import cross_validation

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

def get_test_data(scrambled_data, K, i):
    """ Separates the data and returns the test sample"""
    # if we're not handling the last interval
    if i<K-1:
        test_data = scrambled_data[i*(len(scrambled_data)/K):(i+1)*(len(scrambled_data)/K)]
    else:
        test_data = scrambled_data[i*(len(scrambled_data)/K):]
    
    return test_data

def get_training_data(scrambled_data, K, i):
    """ Separates the data and returns the concatenated K-1 samples for training data"""
    training_data = scrambled_data[0:i*(len(scrambled_data)/K)]

    # if it is not the last interval we still need to add things that follow the test interval
    if i<K-1: 
        training_data = training_data + scrambled_data[(i+1)*(len(scrambled_data)/K):]
    
    return training_data

def get_locations_for_training(scrambled_locations_for_full, scrambled_data, K, i):
    """ Separates the locations from the calculated locations for all data and only returns the ones associated
    to the training data"""
    locations_for_training = scrambled_locations_for_full[0:i*(len(scrambled_data)/K)]

    # if it is not the last interval we still need to add things that follow the test interval
    if i<K-1: 
        locations_for_training = locations_for_training + scrambled_locations_for_full[(i+1)*(len(scrambled_data)/K):]
    return locations_for_training    
    
def predict_locations_for_test_data(training_data, test_data, list_locations_for_training, loc_count):
    list_locations_for_test = []

    # for each test element 
    for test_elem in test_data:
        similarity_to_location = dict()
        # the predicted locations can only be from the ones existing in the training set
        for i in list_locations_for_training:
            if i not in similarity_to_location.keys():
                similarity_to_location[i] = 0.0        
        
        crt = 0
        
        # for each element in the training set
        for training_elem in training_data:
            # calculate similarity between test element and element in training set
            sim = get_similarity(test_elem, training_elem)
            similarity_to_location[list_locations_for_training[crt]] = similarity_to_location[list_locations_for_training[crt]] + sim
            crt = crt + 1
#             print(test_elem,training_elem,sim)

        #normalize similarity (value should be divided to the number of elements that have contributed to it
        contributors = dict()
        for i in range(0,loc_count):
            contributors[i] = 0.0

        for i in range(0,len(training_data)):
            contributors[list_locations_for_training[i]] = contributors[list_locations_for_training[i]] + 1
#         print(list_locations_for_training)
        
#         print("Similarity before: ",similarity_to_location)
#         print("Contributors: ",contributors)
        for crt in range(0,loc_count):
            if crt in similarity_to_location.keys():
                similarity_to_location[crt] = similarity_to_location[crt]/contributors[crt] 
#         print("Similarity after: ",similarity_to_location)    
#         print(similarity_to_location)        
        probable_location_for_test_elem = list_locations_for_training[0]
        for key in similarity_to_location.keys():
            if similarity_to_location[key] < similarity_to_location[probable_location_for_test_elem]:
                probable_location_for_test_elem = key
        
#         print(test_elem, probable_location_for_test_elem)
        list_locations_for_test.append(probable_location_for_test_elem)
    return list_locations_for_test

def randomize_order(data, list_locations_for_full):
    """ Used for randomizing the order of the data in order to be able to randomly chose the k sub samples"""
#     print("Randomizing order: order-scrambled, data-scrambled, locations-scrambled")
    # construct list with elements order
    scrambled_order = []
    for i in range(0,len(data)):
        scrambled_order.append(i)
#     print(scrambled_order)
    
    # scramble order of elements
    random.shuffle(scrambled_order)
#     print(scrambled_order)
    
    # construct new data list with its elements scrambled according to scramble_order
    scrambled_data = []
    for x in scrambled_order:
        scrambled_data.append(data[x])
#     print(data)
#     print(scrambled_data)
    
    # construct new expected locations list with elements scrambled accordingly so that they still mach the data
    scrambled_locations = []
    for x in scrambled_order:
        scrambled_locations.append(list_locations_for_full[x])
#     print(list_locations_for_full)
#     print(scrambled_locations)
    
    return scrambled_data, scrambled_locations, scrambled_order

def unscramble_order(scrambled_data, scrambled_predicted_locations, scrambled_order):
    # make new lists for unscrambled locations and data
    unscrambled_data = []
    unscrambled_locations = []
    for i in range(0,len(scrambled_order)):
        unscrambled_data.append(-1)
        unscrambled_locations.append(-1)
    
    # unscrambled the locations & data
    for i in range(0,len(scrambled_order)):
        unscrambled_data[scrambled_order[i]] = scrambled_data[i]
        unscrambled_locations[scrambled_order[i]] = scrambled_predicted_locations[i]
    
#     print("Unscrambled: data, locations(predicted for all)")
#     print(unscrambled_data)
#     print(unscrambled_locations)
    return unscrambled_data, unscrambled_locations

def estimate_locations_k_fold_cross_validation(K, data, min_loc, max_loc):
    
    """
    # Gets K folding factor and the min_locations and max_locations to consider. Returns best estimated
    # number of locations that can represent the data
    print(K)
    
    full_predictions_accuracy = dict() # keeps how accurate was the estimation for each considered no of locations
    
    for loc_count in range(min_loc, max_loc+1):            
        print("Locations considered: ",loc_count)
        locations_for_full = state_transitions(data, loc_count)
        list_locations_for_full = np.array(locations_for_full).tolist()

        list_scrambled_full_prediction = []
        scrambled_data, scrambled_locations_for_full, scrambled_order = randomize_order(data, list_locations_for_full)
    
        for i in range(0,K):
            test_data = get_test_data(scrambled_data, K, i)
            training_data = get_training_data(scrambled_data, K, i)
            list_scrambled_locations_for_training = get_locations_for_training(scrambled_locations_for_full, scrambled_data, K, i)
                
            # convert locations for training to array, but keep a list copy
            #locations_for_training = np.asarray(list_scrambled_locations_for_training)
                
#             print("Sample "+str(i)+" is test data")
#             print("Scrambled data, scrambled calculated locations, scrambled predicted locations associated")
#             print(scrambled_data)
#             print(scrambled_locations_for_full)
#             print("Scrambled training data and locations associated")
#             print(training_data)
#             print(list_scrambled_locations_for_training)
#             print("Scrambled test data")
#             print(test_data)
#             print("Data, training, test size: ",len(data),len(training_data),len(test_data))
    
            # print("[Locations] Training",list_locations_for_training)
            list_scrambled_predicted_locations_for_test = predict_locations_for_test_data(training_data, test_data, list_scrambled_locations_for_training, loc_count)
            # print("[Locations] Test",list_predicted_locations_for_test)
            list_scrambled_full_prediction = list_scrambled_full_prediction + list_scrambled_predicted_locations_for_test
#             print(list_scrambled_full_prediction)
        
        unscrambled_data, list_full_prediction = unscramble_order(scrambled_data, list_scrambled_full_prediction, scrambled_order)
        print("Unscrambled locations: calculated and predicted for "+str(loc_count)+" locations") 
        print("Calculated locations",list_locations_for_full)
        print("Predicted  locations", list_full_prediction)
        # register the accuracy of the estimation when considering that loc_count is the number of locations (hidden states in HMM0
        full_predictions_accuracy[loc_count] = get_accuracy(list_full_prediction, list_locations_for_full)
        
    # calculating which no of locations was best estimated (we start by considering that it was min_loc)
    best_no_locations_estimated = min_loc
    for key in full_predictions_accuracy.keys():
        # if finding that for another considered no of locations there where fewer errors in the prediction
        if full_predictions_accuracy[key] < full_predictions_accuracy[best_no_locations_estimated]:
            best_no_locations_estimated = key
        # if the estimation is equally good for more locations, we consider the most we can have
        elif full_predictions_accuracy[key] == full_predictions_accuracy[best_no_locations_estimated] and best_no_locations_estimated < key:
            best_no_locations_estimated = key
    print("Prediction accuracy for considered number of hidden states")
    print(full_predictions_accuracy)
    return best_no_locations_estimated
"""
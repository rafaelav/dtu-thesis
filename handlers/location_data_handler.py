'''
Created on Apr 5, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler

import pickle
from sklearn import hmm
import numpy as np
from sklearn import cross_validation
from sklearn import svm
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import datetime
week   = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu',  4:'Fri', 5:'Sat', 6:'Sun'}

DAY_INTERVAL_SECS = 24 * 60 * 60
SECS_IN_MINUTE = 60

def get_utc_from_epoch(epoch_time):
    date_val = datetime.datetime.utcfromtimestamp(int(epoch_time))
    return week[date_val.weekday()]+"\n"+str(date_val.hour)+":"+str(date_val.minute)

def get_xticks_xlabels_from_time(data_start_time, data_end_time, no_of_ticks, between_ticks):    
    dates_epoch = []
    dates_utc = []
    time_to_add_epoch = data_start_time
    
    added = 0
    while added < no_of_ticks:
        timestamp = time_to_add_epoch
        dates_epoch.append(timestamp)
        dates_utc.append(get_utc_from_epoch(timestamp))
        added = added + 1
        time_to_add_epoch = between_ticks*SECS_IN_MINUTE + time_to_add_epoch    
    
    # last time stamp
    timestamp = data_end_time
    dates_epoch.append(timestamp)
    dates_utc.append(get_utc_from_epoch(timestamp))
        
    return dates_epoch, dates_utc

def plot_locations(list_locations_over_time_bins, days_to_consider, time_bin, username, colors_dict, start_time, end_time, plot_time_interval, loc_type, file_path):
    print("Time bins: ",len(list_locations_over_time_bins))
    # get locations count
    locations_count = 1 + max(np.array(list_locations_over_time_bins).tolist())
    print("Locations identified: ",locations_count)
    
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)       
     
    plt.xlim(start_time,end_time)
    crt = start_time
    print(list_locations_over_time_bins)
    list_locations_over_time_bins = np.array(list_locations_over_time_bins).tolist()
    #print(list_locations_over_time_bins)
    for loc in list_locations_over_time_bins:
        #print(loc, crt, crt+time_bin*SECS_IN_MINUTE - 1, colors_dict[loc])
        plt.plot([crt,crt+time_bin*SECS_IN_MINUTE - 1], [0,0], '-',linewidth=50, color=colors_dict[loc])
        crt = crt+time_bin*SECS_IN_MINUTE

    #plt.ylim(0)
    plt.title("Locations from "+loc_type+" data. Plot over (days): "+str(days_to_consider)+" User: "+username)
    plt.xlabel("Locations in time", fontsize=10)
    
    no_of_ticks = (end_time - start_time)/(plot_time_interval*SECS_IN_MINUTE) + 1
    #print(plot_time_interval,no_of_ticks)
    ticks, labels_utc = get_xticks_xlabels_from_time(start_time, end_time, no_of_ticks, plot_time_interval)#(dates_epoch, no_of_ticks)
    
    plt.xticks(ticks, labels_utc, rotation = 90)
    plt.yticks([2], [""])
    fig.tight_layout()    
    fig.savefig(file_path)
#     if loc_type == "hmm":
#         fig.savefig("../../plots/"+username+"/"+"hmm_locations_("+str(locations_count)+")_"+str(days_to_consider)+"days_plot.png")
#     elif loc_type == "kmeans":
#         fig.savefig("../../plots/"+username+"/"+"kmeans_locations_("+str(locations_count)+")_"+str(days_to_consider)+"days_plot.png")

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
    #end_time = user_data[len(user_data)-1][1]
    end_time = start_time + days_to_consider * DAY_INTERVAL_SECS
    
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

def state_transitions(matrix, loc_count, loc_type):
    if loc_type == "hmm":
        model = hmm.GaussianHMM(loc_count, "full")
        #print(matrix_with_bssids_on_columns)
        X = np.array(matrix)
        model.fit([X])
        result = model.predict(X)
    elif loc_type == "kmeans":
        n_clusters=loc_count
        init='k-means++'
        n_init=10
        max_iter=500
        tol=0.0001
        precompute_distances=True
        verbose=0
        random_state=None
        copy_x=True
        n_jobs=1    
        
        kmeans = KMeans(n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs)
        result = kmeans.fit_predict(matrix)
    else:
        result = None
    return result
    

def estimate_locations_k_fold_cross_validation(K, matrix, min_loc, max_loc, loc_type):
    max_score = 0.0
    estimated_locations = 0
    transitions = []
    # for cross validation with K fold, cv is K, X is matrix and y is expected
    for loc in range(min_loc, max_loc+1):
        expected = state_transitions(matrix, loc, loc_type)
        print("Considering "+str(loc)+" locations, expected division is:")
        print(expected)
        expected = np.array(expected).tolist()
        #print("Locations: "+str(loc))
        #print(expected)
                 
        X = np.array(matrix)
        y = np.array(expected)
        
        clf = svm.SVC(kernel='linear', C=1)
        scores = cross_validation.cross_val_score(clf, X, y, cv=K)
    
        print(scores)
        avg_score = 0.0
        for x in scores:
            avg_score = avg_score + x
        avg_score = avg_score/len(scores)
        
        if avg_score > max_score:
            max_score = avg_score
            estimated_locations = loc
            transitions = expected
        if avg_score == max_score and estimated_locations < loc:
            max_score = avg_score
            estimated_locations = loc
            transitions = expected
            
    print("Accuracy (score, number of estimated locations): ")
    print(max_score, estimated_locations)
    return estimated_locations, transitions    

def get_locations_found(loc_over_time_list):
    """
    Receives a list of x values. Value at position i represent the location identified at time bin i.
    Returns the maximum + 1 number found (which represents the number of locations identified in the list) 
    """
    
    locations = max(loc_over_time_list) + 1
    return locations
# def state_transitions_kmeans(matrix, loc_count):
#     n_clusters=loc_count
#     init='k-means++'
#     n_init=10
#     max_iter=500
#     tol=0.0001
#     precompute_distances=True
#     verbose=0
#     random_state=None
#     copy_x=True
#     n_jobs=1    
#     
#     kmeans = KMeans(n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs)
#     result = kmeans.fit_predict(matrix)
#     return result    
# 
# def estimate_locations_k_fold_cross_validation_with_kmeans(K, matrix, min_loc, max_loc):
#     max_score = 0.0
#     estimated_locations = 0
#     transitions = []
#     # for cross validation with K fold, cv is K, X is matrix and y is expected
#     for loc in range(min_loc, max_loc+1):
#         expected = state_transitions_kmeans(matrix, loc)
#         print("Considering "+str(loc)+" locations, expected division is:")
#         print(expected)
#         expected = np.array(expected).tolist()
#         #print("Locations: "+str(loc))
#         #print(expected)
#                  
#         X = np.array(matrix)
#         y = np.array(expected)
#         
#         clf = svm.SVC(kernel='linear', C=1)
#         scores = cross_validation.cross_val_score(clf, X, y, cv=K)
#     
#         print(scores)
#         avg_score = 0.0
#         for x in scores:
#             avg_score = avg_score + x
#         avg_score = avg_score/len(scores)
#         
#         if avg_score > max_score:
#             max_score = avg_score
#             estimated_locations = loc
#             transitions = expected
#     print("Accuracy (score, number of estimated locations): ")
#     print(max_score, estimated_locations)
#     return estimated_locations, transitions    
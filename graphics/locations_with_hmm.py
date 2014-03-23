'''
Created on Mar 23, 2014

@author: rafa
'''
import pickle
from sklearn import hmm
import numpy as np

def load_pickled_matrix(filename):
    pickled_data = pickle.load(open(filename, "rb" ))
    #print(pickled_data)
    return pickled_data

def create_matrix_for_hmm(presence_matrix):
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

base = "../../plots/"
days_to_consider = 2
treshold = 0.5

for i in range (1,2):
    username = "user_"+str(i)+"_sorted"
    fig_filename = base+username+"/"+"locations_graph_"+str(days_to_consider)+"days.pdf"
    matrix_file = base+username+"/"+"pickled_matrix_"+username+"_"+str(days_to_consider)+"days.p"

    # load the presence matrix for signals for all bssid in 5 min time bins
    presence_matrix = load_pickled_matrix(matrix_file)
    matrix_with_bssids_on_columns, bssids_order = create_matrix_for_hmm(presence_matrix)
    print(len(bssids_order))
    print(len(matrix_with_bssids_on_columns))
    model2 = hmm.GaussianHMM(32) # up tp 25 without 23
    """#x=["1,0", "1,5", "1,4", "10,1", "32,1", "1,3", "1,13"]
    x=[0, 5, 4, 10, 32, 3, 13, 23, 2, 0, 7, 0, 4, 5, 46, 47]
    c = [[0],[5],[4]]
    y = [[1, 2, 1], [3, 4, 2], [1,1,0.175], [1,1,0.175]]
    a=np.array(x)
    a = np.array(y)
    #a = np.atleast_2d(y)
    print(a)
    #b=a[:,np.newaxis]
    #print(b)
    model2.fit([a])
    Z2 = model2.predict(a)
    print(model2.score(a))
    print(Z2)"""
    
    #print(matrix_with_bssids_on_columns)
    X = np.array(matrix_with_bssids_on_columns)
    print(X)
    #Y = X[:,np.newaxis]
    #print(Y)
    model2.fit([X])
    Z2 = model2.predict(X)
    print(Z2)
'''
Created on May 9, 2014

@author: rafa
'''
from sklearn import cluster
import sys
sys.path.append( ".." )
from handlers import location_data_handler

X = [[1,1,1,0,0,0],
[1,1,1,0,0,0],
[1,1,0,0,0,0],
[0,0,0,1,1,1],
[0,0,0,1,1,0],
[0,0,0,1,1,1],
[0,0,1,1,1,0],
[0,0,1,1,1,0]]

base = "../../plots/"
user_file = "user_6_sorted"
days_to_consider = 1
estimated_locations_file = base+user_file+"/"+"estimated_locations_"+user_file+"_"+str(days_to_consider)+"days.p"
pickled_matrix_file = base+user_file+"/"+"pickled_matrix_all_"+user_file+"_"+str(days_to_consider)+"days.p"
estimated_states = location_data_handler.load_pickled_file(estimated_locations_file)
print(user_file, estimated_states)

# load matrix
presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)
    
# make presence matrix for hmm
hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(presence_matrix)

n_clusters=estimated_states
init='k-means++'
n_init=10
max_iter=500
tol=0.0001
precompute_distances=True
verbose=0
random_state=None
copy_x=True
n_jobs=1
 
kmeans = cluster.KMeans(n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs)
result = kmeans.fit_predict(hmm_matrix)
print(result)
'''
Created on Jul 20, 2014

@author: rafa
'''
import pickle

def load_pickled_matrix(filename):
    pickled_data = pickle.load(open(filename, "rb" ))
    #print(pickled_data)
    return pickled_data

my_file = "../../plots/user_6_sorted/pickled_matrix_all_user_6_sorted_1days.p"

data = load_pickled_matrix(my_file)
print(data)
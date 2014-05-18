'''
Created on May 18, 2014

@author: rafa
'''

# USED ONLY FOR TESTING STUFF

import pickle

base = "../../plots/"+"user_6_sorted"+"/"
def load_pickled_file(filename):
    pickled_data = pickle.load(open(filename, "rb" ))
    return pickled_data
# 
# data = load_pickled_file(base+"day1.p")
# print(data)
# 
# data = load_pickled_file(base+"day_0_transitions.p")
# print(data)

data = load_pickled_file(base+"day2.p")
print(data)
 
data = load_pickled_file(base+"day_1_transitions.p")
print(data)


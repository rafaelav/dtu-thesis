'''
Created on May 18, 2014

@author: rafa
'''
import datetime
import sys
sys.path.append( ".." )

from handlers import match_handler

user_list = [6]
start_day = 0
days_to_consider = 2 # in total
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5
iterations = 10 # number of times it runs hmm before trying to figure out best estimation
step = 1 # number of days to consider in one interval
min_loc = 2
max_loc = 10
threshold = 0.98

for user in user_list:
    user_file = "user_"+str(user)+"_sorted"
    # generate transition files for given days
    
#     start_moment = datetime.datetime.now()
#     
#     print("Creating transitions for ",user_file)
#     match_handler.calculate_transitions_over_time(user_file, start_day, days_to_consider, step, m_most_popular_bssids, time_bin, plot_interval, iterations, min_loc, max_loc)
# 
#     print("Start time: "+str(start_moment))
#     print("End time: "+str(datetime.datetime.now()))
    
    # get the associations
    associations = match_handler.make_location_associations(user_file, start_day, days_to_consider, step, threshold)
    print(associations[0])
#     print("HERE")
#     crt = 0
#     for elem in associations[0]:
#         print("day 0, location "+str(crt),elem[0])
#         crt = crt +1
#         
#     crt = 0
#     for elem in associations[1]:
#         print("day 1, location "+str(crt),elem[0])
#         crt = crt +1    

    # make transitions for all given days considering the location associations that have been identified
    
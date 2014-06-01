'''
Created on May 18, 2014

@author: rafa
'''
import datetime
import sys
sys.path.append( ".." )

from handlers import match_handler
from handlers import user_data_handler

user_list = [6]
start_day = 0
days_to_consider = 30 # in total
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5
iterations = 10 # number of times it runs hmm before trying to figure out best estimation
step = 1 # number of days to consider in one interval
min_loc = 2
max_loc = 10
threshold = 0.95

for user in user_list:
    user_file = "user_"+str(user)+"_sorted"
    # generate transition files for given days
    
    start_moment = datetime.datetime.now()
     
    print("Creating transitions for ",user_file)
    match_handler.calculate_transitions_over_time(user_file, start_day, days_to_consider, step, m_most_popular_bssids, time_bin, plot_interval, iterations, min_loc, max_loc)
    end_transitions = datetime.datetime.now()
        
    # get the associations
    associations = match_handler.make_location_associations(user_file, start_day, days_to_consider, step, threshold)
    end_associations = datetime.datetime.now()
    #print(associations[0])
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
    combined_locations = match_handler.combine_locations_with_correct_associations(user_file, start_day, days_to_consider, step, associations)
    end_combining = datetime.datetime.now()

    print("Start time: "+str(start_moment))
    print("End time creating transitions: "+str(datetime.datetime.now()))
    print("End time creating associations: "+str(datetime.datetime.now()))
    print("End time creating combinations: "+str(datetime.datetime.now()))
    
    # plot
#     user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)    
#     start_time = user_data[0][1]
#     end_time = user_data[len(user_data)-1][1]
    #NOT WORKINGmatch_handler.plot_combined_transitions(user_file, time_bin, start_day, days_to_consider, step, plot_interval, start_time,end_time)
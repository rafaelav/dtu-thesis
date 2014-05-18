'''
Created on May 18, 2014

@author: rafa
'''
import datetime
import sys
sys.path.append( ".." )

from handlers import match_handler

user_list = [6]
start_day = 1
days_to_consider = 1
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5
iterations = 10 # number of times it runs hmm before trying to figure out best estimation

for user in user_list:
    user_file = "user_"+str(user)+"_sorted"
    # generate transition files for given days
    print("Creating transitions for ")
    match_handler.calculate_transitions_over_time(user_file, start_day, days_to_consider, m_most_popular_bssids, time_bin, iterations)

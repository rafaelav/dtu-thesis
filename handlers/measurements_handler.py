'''
Created on Jun 1, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
from math import log

BINS_PER_DAY = 288 #5 min time bins

def random_entropy(user_filename, loc_over_time_list):
    loc_count = location_data_handler.get_locations_found(loc_over_time_list)
    rand_entropy = log(loc_count,2)
    print("Random entropy - "+user_filename+": "+str(rand_entropy))
    return rand_entropy

def temporal_uncorrelated_entropy(user_filename, loc_over_time_list, no_of_days, type):
    loc_count = location_data_handler.get_locations_found(loc_over_time_list)
    tu_entropy = 0
    
    if type == "app_loc":
        # case 0 - calculated as location_nr_of_non_tied_to_eachother_aparitions/nr_of_non_tied_to_eachother_apparitions
        for i in range(0,loc_count):
            probability_over_bins = get_probability_of_apparition_over_locations(i, loc_over_time_list)
            tu_entropy = tu_entropy - probability_over_bins * log(probability_over_bins,2)
        
    elif type == "app_bins":
        # case 1 - calculated as location_nr_of_aparitions/nr_of_bins
        for i in range(0,loc_count):
            probability_over_bins = get_probability_of_apparition_over_bins(i, loc_over_time_list)
            tu_entropy = tu_entropy - probability_over_bins * log(probability_over_bins,2)
    
    elif type == "app_days":    
        # case 2 - calculated as location_nr_of_non_tied_to_eachother_aparitions/nr_of_days
        for i in range(0,loc_count):
            probability_over_days = get_probability_of_apparition_over_days(i, loc_over_time_list,no_of_days)
            tu_entropy = tu_entropy - probability_over_days * log(probability_over_days,2)
    elif type == "indiv_app_days":
        # case 3 - calculated as nr of times locations has appeared over the days (considering    
        # just true or false if it appears during a day) divided to no of days 
        for i in range(0,loc_count):
            probability_indiv_over_days = get_probability_of_individual_apparition_over_days(i, loc_over_time_list, no_of_days)
            tu_entropy = tu_entropy - probability_indiv_over_days * log(probability_indiv_over_days,2)
    
    return tu_entropy
    
# BEST OPTION
def get_probability_of_apparition_over_locations(loc, loc_over_time_list):
    probability = 0
    total_locations = 0
    prev = -1 
    
    for x in loc_over_time_list:
        if loc == x and prev != loc: # if it's the current location and it is just starting (we count as one time appearance all time bins that are the same and consecutive)
            probability = probability + 1
        if prev != x:
            total_locations = total_locations + 1
        prev = x
    
    print(probability,total_locations)
    probability = (probability+0.0)/total_locations

    return probability

def get_probability_of_apparition_over_bins(loc, loc_over_time_list):
    probability = 0
    for x in loc_over_time_list:
        if loc == x:
            probability = probability + 1
    
    #print(probability, len(loc_over_time_list))
    probability = (probability+0.0)/len(loc_over_time_list)
    
    return probability

def get_probability_of_apparition_over_days(loc, loc_over_time_list, no_of_days):
    probability = 0
    prev = -1 
    
    for x in loc_over_time_list:
        if loc == x and prev != loc: # if it's the current location and it is just starting (we count as one time appearance all time bins that are the same and consecutive)
            probability = probability + 1
        prev = x
    
    #print(probability,no_of_days)
    probability = (probability+0.0)/no_of_days

    return probability

def get_probability_of_individual_apparition_over_days(loc, loc_over_time_list, no_of_days):
    probability = 0
    count = -1
    appeared = False
    
    for x in loc_over_time_list:
        count = count + 1
        if count >= BINS_PER_DAY: # mived_to_next_day
            appeared = False
            count = 0

        if appeared == False and loc == x:
            probability = probability + 1
            appeared = True
    
    print(probability,no_of_days)
    probability = (probability+0.0)/no_of_days

    return probability

my_list = location_data_handler.load_pickled_file("../../plots/user_6_sorted/star_day_0_step_1_days_30_combined_transitions.p")
print(my_list)
#prob = get_probability_of_individual_apparition_over_days(3, my_list,1)
#print(prob)
tu_entr = temporal_uncorrelated_entropy("user_6_sorted", my_list, 1, "app_loc")
print(tu_entr)
rand_entr = random_entropy("user_6_sorted", my_list)
print(rand_entr)
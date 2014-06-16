'''
Created on Jun 1, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
#from sympy import log
from math import log
import sympy as sy

BINS_PER_DAY = 288 #5 min time bins

def get_number_of_possible_intervals(sequence_len, number_of_elements):
    return number_of_elements - sequence_len + 1

def build_sequence(sequence_len, start_pos, loc_over_time_list):
    print(start_pos,sequence_len)
    return loc_over_time_list[start_pos, sequence_len+start_pos]

def actual_entropy_with_bins(user_filename, loc_over_time_list, no_of_days):
    result = 0
    print("For user: "+user_filename)
    
#    min_sequence_length = 1
#    max_sequence_length = BINS_PER_DAY * no_of_days

    min_sequence_length = 2
    max_sequence_length = 3    
    
    for sequence_len in range(min_sequence_length, max_sequence_length):
        list_found_sequences = []
        list_count_apparitions_of_sequences = []
        
        start_pos = 0
        
        while start_pos+sequence_len <= len(loc_over_time_list):
            sequence = build_sequence(sequence_len, start_pos, loc_over_time_list)
            print("Start seq: "+str(start_pos)+" Int len: "+str(sequence_len))
            print(" Seq: ",sequence)
            if sequence in list_found_sequences:
                list_count_apparitions_of_sequences[list_found_sequences.index(sequence)] += 1 
            else:
                list_found_sequences.append(sequence)
                list_count_apparitions_of_sequences.append(0)
            
        intervals_count = get_number_of_possible_intervals(sequence_len, len(loc_over_time_list))
        print("Number of possible intervals: "+str(intervals_count))
        
        print("Found sequences and the number of times they appeared ")
        print(list_found_sequences)
        print(list_count_apparitions_of_sequences)
        
        crt = 0
        for x in list_found_sequences:
            probability = list_count_apparitions_of_sequences[crt]/intervals_count
            result = result - probability*log(probability,2)
    
    print("Result: ", result)
    return result
        
            

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
def get_max_predictability(S, N):
#     x=sy.Symbol('x')
#     eq = (-1)*x*log(x,2)-(1-x)*log((1-x),2)+(1-x)*log((N-1),2)-S
#     print(sy.solve(logcombine(eq, force=True)))

    # predictability can only be a number between 0 and 1
    x = 0.99
    closest_val = 1000
    result = x
    while x >= 0:
        if 1-x<0:
            print(x)
        difference = abs((-1)*x*log(x,2)-(1-x)*log((1-x),2)+(1-x)*log((N-1),2)-S)
        print("For "+str(x)+" dif is "+str(difference)+" crt closest val "+str(closest_val)+" result: "+str(result))
        if difference < closest_val:
            closest_val = difference
            result = x
        x = x - 0.01
    result = result * 100 
    if result % 10 == 9:
        result = (result + 1.0)/100
    else:
        result = (result +0.0)/100
        
    print(result, closest_val)
    #print(sympy.solve(pow(N-1,1-x)/(pow(2,S)*x*pow(1-x,1-x)) - 1))

# my_list = location_data_handler.load_pickled_file("../../plots/user_6_sorted/star_day_0_step_1_days_30_combined_transitions.p")
# print(my_list)
# #prob = get_probability_of_individual_apparition_over_days(3, my_list,1)
# #print(prob)
# tu_entr = temporal_uncorrelated_entropy("user_6_sorted", my_list, 1, "app_loc")
# print(tu_entr)
# rand_entr = random_entropy("user_6_sorted", my_list)
# print(rand_entr)

#get_max_predictability(0.8, 50)

actual_entropy_with_bins("test", [1,2,3,4,1,2,3,1,2], 1)
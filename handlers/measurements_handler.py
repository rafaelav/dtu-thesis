'''
Created on Jun 1, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
#from sympy import log
from math import log
#import sympy as sy

BINS_PER_DAY = 288 #5 min time bins
INTERVALS_PER_DAY = 24

def get_number_of_possible_intervals(sequence_len, number_of_elements):
    return number_of_elements - sequence_len + 1

def build_sequence(sequence_len, start_pos, loc_over_time_list):
    return loc_over_time_list[start_pos: sequence_len+start_pos]

def actual_entropy_with_bins(user_filename, loc_over_time_list, no_of_days, max_previous):
    #result = 0
    print("For user: "+user_filename)
    
    min_sequence_length = 2
    max_sequence_length = max_previous#BINS_PER_DAY * no_of_days

#    min_sequence_length = 2
#    max_sequence_length = 3    
    
    entropies=dict()
    for sequence_len in range(min_sequence_length, max_sequence_length):
        entropies[sequence_len]=0
        print("Len of sequences: "+str(sequence_len))
        list_found_sequences = []
        list_count_apparitions_of_sequences = []
        
        start_pos = 0
        
        while start_pos+sequence_len <= len(loc_over_time_list):
            sequence = build_sequence(sequence_len, start_pos, loc_over_time_list)
            #print("Start seq: "+str(start_pos)+" Int len: "+str(sequence_len))
            #print(" Seq: ",sequence)
            if sequence in list_found_sequences:
                list_count_apparitions_of_sequences[list_found_sequences.index(sequence)] = list_count_apparitions_of_sequences[list_found_sequences.index(sequence)] + 1 
            else:
                list_found_sequences.append(sequence)
                list_count_apparitions_of_sequences.append(1)
            start_pos = start_pos + 1
            
        intervals_count = get_number_of_possible_intervals(sequence_len, len(loc_over_time_list))
        #print("Number of possible intervals: "+str(intervals_count))
        
        #print("Found sequences and the number of times they appeared ")
        #print(list_found_sequences)
        #print(list_count_apparitions_of_sequences)
        
        crt = 0
        for x in list_found_sequences:
            probability = (list_count_apparitions_of_sequences[crt]+0.0)/intervals_count
            #print("probability: ",probability)
            entropies[sequence_len] = entropies[sequence_len] - probability*log(probability,2)
            #####result = result - probability*log(probability,2)
            crt = crt + 1
    
    print(entropies)
    minimum_entropy = entropies[2]
    prev_states = 2
    for key in entropies:
        if minimum_entropy>entropies[key]:
            minimum_entropy = entropies[key]
            prev_states = key
            
    print("Result entro/states: ", minimum_entropy, prev_states)
    return minimum_entropy, prev_states

def get_mostly_present_location(sequence):
    elements = []
    apparitions = []
    
    for x in sequence:
        if x in elements:
            apparitions[elements.index(x)]=apparitions[elements.index(x)] + 1 
        else:
            elements.append(x)
            apparitions.append(1)
    crt = 0
    max_val = 0
    location = 0
    
    for x in elements:
        #if x != elements[crt]:
            #print("ERROR")
        if apparitions[crt] > max_val:
            max_val = apparitions[crt]
            location = x
        crt = crt + 1
    
    return location
    
def convert_to_combined_bins(loc_over_time_list, bins_per_day):
    """ Combines bins so that we have only bins_per_day number of bins in each day. Combination
    is done by determining how many bins need to be combined and selecting as location instead of
    the locations in that sequence of bins, the location that mostly appeares among them"""
    result = []
    start_pos = 0
    how_many_to_combine = 288 / bins_per_day
    while start_pos+how_many_to_combine <= len(loc_over_time_list):
        subsequence = build_sequence(how_many_to_combine, start_pos, loc_over_time_list)
        combined_location = get_mostly_present_location(subsequence) # the location that appears the most
        #print(combined_location,subsequence)
        result.append(combined_location)
        start_pos = start_pos + how_many_to_combine
    #print(len(result),len(loc_over_time_list)/how_many_to_combine)
    return result

def actual_entropy_with_combined_bins(user_filename, loc_over_time_list, no_of_days, bins_per_day, max_previous):
    """
    Using hourly bins to calculate entropy. Grouping every consecutive 12 bins (bins in an hour if
    bins are 5 mins long) and attributing the location that mostly appeares in them.
    """
    #print(loc_over_time_list)
    loc_over_time_list = convert_to_combined_bins(loc_over_time_list, bins_per_day)
    #print(loc_over_time_list)
    
    result = 0
    #print("For user: "+user_filename)
    
    min_sequence_length = 1
    max_sequence_length = max_previous#bins_per_day * no_of_days
    
    entropies=dict()
    for sequence_len in range(min_sequence_length, max_sequence_length):
        entropies[sequence_len]=0
        print("Len of sequences: "+str(sequence_len))
        list_found_sequences = []
        list_count_apparitions_of_sequences = []
        
        start_pos = 0
        
        while start_pos+sequence_len <= len(loc_over_time_list):
            sequence = build_sequence(sequence_len, start_pos, loc_over_time_list)
            #print("Start seq: "+str(start_pos)+" Int len: "+str(sequence_len))
            #print(" Seq: ",sequence)
            if sequence in list_found_sequences:
                list_count_apparitions_of_sequences[list_found_sequences.index(sequence)] = list_count_apparitions_of_sequences[list_found_sequences.index(sequence)] + 1 
            else:
                list_found_sequences.append(sequence)
                list_count_apparitions_of_sequences.append(1)
            start_pos = start_pos + 1
        
#         no_aps = 0
#         for ap in list_count_apparitions_of_sequences:
#             no_aps = no_aps + ap
            
        intervals_count = get_number_of_possible_intervals(sequence_len, len(loc_over_time_list))
#         if no_aps != intervals_count:
#             print("ERROR")
#             return
        
#         print("Number of possible intervals: "+str(intervals_count))
#         
#         print("Found sequences and the number of times they appeared ")
#         print(list_found_sequences)
#         print(list_count_apparitions_of_sequences)
        
        crt = 0
        for x in list_found_sequences:
            probability = (list_count_apparitions_of_sequences[crt]+0.0)/intervals_count
            #print("probability: ",probability)
            #print(probability*log(probability,2),probability,list_count_apparitions_of_sequences[crt],x)
            #print(log(probability,2))
            result = result - probability*log(probability,2)
            entropies[sequence_len] = entropies[sequence_len] - probability*log(probability,2)
            #print(probability*log(probability,2))
            crt = crt + 1
        #print("Partial result: "+str(result))

    print(entropies)
    minimum_entropy = entropies[1]
    prev_states = 1
    for key in entropies:
        if minimum_entropy>entropies[key]:
            minimum_entropy = entropies[key]
            prev_states = key
            
    print("Result entro/states: ", minimum_entropy, prev_states)
    return minimum_entropy, prev_states, result
        
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
    
    # THIS 
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

# THIS
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

my_list = location_data_handler.load_pickled_file("../../plots/user_19_sorted/star_day_0_step_1_days_30_combined_transitions.p")
#actual_entropy_with_bins("test", my_list, 30)

#my_list = location_data_handler.load_pickled_file("../../plots/user_6_sorted/day_1_count_1_transitions.p")
#my_list = [1,2,3,4,5,6,7,8,9,10,11,12]
tu_entr = temporal_uncorrelated_entropy("user_6_sorted", my_list, 30, "app_bins")
print(tu_entr)
actual_entropy_with_combined_bins("user_6_sorted", my_list, 30, 24, 2)

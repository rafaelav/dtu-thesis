'''
Created on Jun 20, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
from handlers import measurements_handler

user_list = [6]
max_previous_conditional_entropy = 3
max_previous_full_entropy = -1
bins_per_day = 24#*12
base = "../../plots/"
file_name = "/star_day_0_step_1_days_30_combined_transitions.p"
no_of_days = 30
tu_entro_type = "app_bins"

for user in user_list:
    username = "user_"+str(user)+"_sorted"
    locations_file = base+username+file_name
    
    loc_over_time_list = location_data_handler.load_pickled_file(locations_file)
    
    if bins_per_day != 24 * 12:
        loc_over_time_list = measurements_handler.convert_to_combined_bins(loc_over_time_list, bins_per_day)
    
    # calculating random entropy ( it is calculate with locations for 5 min bins only)
    rand_entropy = measurements_handler.random_entropy(username, loc_over_time_list)
    
    # calculating temp uncorrel entropy
    tu_entropy = measurements_handler.temporal_uncorrelated_entropy(username, loc_over_time_list, no_of_days, tu_entro_type)
    
    # calculating full entropy 
#    if max_previous_full_entropy != -1:
#        full_entropy = measurements_handler.actual_entropy_with_combined_bins(username, loc_over_time_list, max_previous_full_entropy)
#    else:
#        full_entropy = measurements_handler.actual_entropy_with_combined_bins(username, loc_over_time_list)
        
    # calculating conditional entropy
    if max_previous_conditional_entropy!=-1:
        entropies, minimum_cond_entropy, no_of_known_states, sum_of_all_possibilities, media = measurements_handler.conditional_entropy(username, loc_over_time_list, max_previous_conditional_entropy)
    else:
        entropies, minimum_cond_entropy, no_of_known_states, sum_of_all_possibilities, media = measurements_handler.conditional_entropy(username, loc_over_time_list)        
    
    # calculating predictability - again..only with all locations in 30 days
    no_locations = location_data_handler.get_locations_found(loc_over_time_list)
    #predictability, how_close_to_0 = measurements_handler.get_max_predictability(entropies[1], no_locations)
    predictability, how_close_to_0 = measurements_handler.get_max_predictability(media, no_locations)
    
    #print("Random, temporal-uncorrelated, full, minimum conditional, sum of all possibilities",rand_entropy, tu_entropy, full_entropy, minimum_cond_entropy, sum_of_all_possibilities)
    print("Random, temporal-uncorrelated, full, minimum conditional, sum of all possibilities",rand_entropy, tu_entropy, media)
    print("Max predictability: ",predictability)
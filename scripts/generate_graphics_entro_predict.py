'''
Created on Jun 20, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
from handlers import measurements_handler
import pickle

user_list = [4,6,7,11,12,14,17,19,20,24,25,27,32,34,35,36,37,38,39,40,41,44,45,46,48,49,50,52,53,55,57,58,59,60,62,70,72,74,75]
max_previous_conditional_entropy = -1
max_previous_full_entropy = -1
bins_per_day = 24*2
base = "../../plots/"
base_entro_pred = "entro_pred_2/"
file_full_entropies = base+base_entro_pred+"full_entropies.p"
file_rand_entropies = base+base_entro_pred+"rand_entropies.p"
file_tu_entropies = base+base_entro_pred+"tu_entropies.p"
file_cond_entropies = base+base_entro_pred+"cond_entropies.p"
file_pred = base+base_entro_pred+"pred.p"
file_name = "/star_day_0_step_1_days_30_combined_transitions.p"
no_of_days = 30
tu_entro_type = "app_bins"

dict_user_full_entro = dict()
dict_user_rand_entro = dict()
dict_user_tu_entro = dict()
dict_user_conditional_entros = dict()
dict_user_predict = dict()

def generate_measurements_and_save_results():
    for user in user_list:
        print("Start for user "+str(user))
        username = "user_"+str(user)+"_sorted"
        locations_file = base+username+file_name
        
        loc_over_time_list = location_data_handler.load_pickled_file(locations_file)
        
        if bins_per_day != 24 * 12:
            loc_over_time_list = measurements_handler.convert_to_combined_bins(loc_over_time_list, bins_per_day)
        
        # calculating random entropy ( it is calculate with locations for 5 min bins only)
        rand_entropy = measurements_handler.random_entropy(username, loc_over_time_list)
        
        # calculating temp uncorrel entropy
        print("TU entropy")
        tu_entropy = measurements_handler.temporal_uncorrelated_entropy(username, loc_over_time_list, no_of_days, tu_entro_type)
        
        # calculating full entropy 
    #    if max_previous_full_entropy != -1:
    #        full_entropy = measurements_handler.actual_entropy_with_combined_bins(username, loc_over_time_list, max_previous_full_entropy)
    #    else:
    #        full_entropy = measurements_handler.actual_entropy_with_combined_bins(username, loc_over_time_list)
            
        # calculating conditional entropy
        print("Cond entro")
        if max_previous_conditional_entropy!=-1:
            entropies, minimum_cond_entropy, no_of_known_states, sum_of_all_possibilities, media = measurements_handler.conditional_entropy_version2(username, loc_over_time_list, max_previous_conditional_entropy)
        else:
            entropies, minimum_cond_entropy, no_of_known_states, sum_of_all_possibilities, media = measurements_handler.conditional_entropy_version2(username, loc_over_time_list)        
        
        # save all entries for user
        dict_user_rand_entro[user] = rand_entropy
        dict_user_tu_entro[user] = tu_entropy
        dict_user_full_entro[user] = media
        dict_user_conditional_entros[user] = entropies
        
        # calculating predictability - again..only with all locations in 30 days
        no_locations = location_data_handler.get_locations_found(loc_over_time_list)
        #predictability, how_close_to_0 = measurements_handler.get_max_predictability(entropies[1], no_locations)
        #predictability, how_close_to_0 = measurements_handler.get_max_predictability(media, no_locations)
        predictability = measurements_handler.get_max_predictability_version2(media, no_locations)
        #save predictability for each user
        dict_user_predict[user] = predictability
        
        #print("Random, temporal-uncorrelated, full, minimum conditional, sum of all possibilities",rand_entropy, tu_entropy, full_entropy, minimum_cond_entropy, sum_of_all_possibilities)
        print("Random, temporal-uncorrelated, full, minimum conditional, sum of all possibilities",rand_entropy, tu_entropy, media)
        print("Max predictability: ",predictability)
        
        pickle.dump(dict_user_full_entro, open(file_full_entropies, "wb"))
        pickle.dump(dict_user_tu_entro, open(file_tu_entropies, "wb"))
        pickle.dump(dict_user_rand_entro, open(file_rand_entropies, "wb"))
        pickle.dump(dict_user_conditional_entros, open(file_cond_entropies, "wb"))
        pickle.dump(dict_user_predict, open(file_pred, "wb"))

import matplotlib.pyplot as plt
from numpy.random import normal

def generate_entro_distribution(file_in_which_to_save):
    full_entro_dict = pickle.load(open(file_full_entropies, "rb" ))
    numbers = []
    for key in full_entro_dict.keys():
        numbers.append(round(full_entro_dict[key],2))
    unique_numbers = []
    for x in numbers:
        if x not in unique_numbers:
            unique_numbers.append(x)
    no_bins = len(unique_numbers)
    print(no_bins)
        
    print(numbers)
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)  
    #plt.title("Gaussian Histogram")
    plt.xlabel("Entropy value")
    plt.ylabel("Frequency distribution")    
    plt.hist(numbers, bins=no_bins, normed=True)
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)
    
    
def generate_conditioned_entro_graphic(user_list_cond_graphic):
    stuff = 1

def generate_averages():
    stuff = 1

def generate_pred_distribution():
    stuff = 1
    
generate_measurements_and_save_results()
#generate_entro_distribution(base+base_entro_pred+"full_entro_distrib.png")
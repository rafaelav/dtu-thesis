'''
Created on Jun 20, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_data_handler
from handlers import measurements_handler
import pickle

#user_list = [4,6,7,11,12,14,17,19,20,24,25,27,32,34,35,36,37,38,39,40,41,44,45,46,48,49,50,52,53,55,57,58,59,60,62,70,72,74,75,80,82,83,91,92,99,100,102,103,105,108,110,111,113,114,116,117,118,119,120,123,124,125,126,129,130]
user_list = [4,25,34,48,49,59,118,125]
max_previous_conditional_entropy = -1
max_previous_full_entropy = -1
bins_per_day = 24*2
base = "../../plots/"
base_entro_pred = "entro_pred_selected_estimations/"#"entro_pred_full_estimations/"#"entro_pred_full_after_match_mod/"
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
        if max_previous_full_entropy != -1:
            full_entropy = measurements_handler.actual_entropy_with_combined_bins(username, loc_over_time_list, max_previous_full_entropy)
        else:
            full_entropy = measurements_handler.actual_entropy_with_combined_bins(username, loc_over_time_list)
            
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
import numpy as np
from scipy.interpolate import UnivariateSpline


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
    plt.xlabel("S value", fontsize=18)
    plt.ylabel("Frequency", fontsize=18)    
    plt.hist(numbers, bins=no_bins, normed=False)
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)
    
def generate_rand_entro_distribution(file_in_which_to_save):
    full_entro_dict = pickle.load(open(file_rand_entropies, "rb" ))
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
    plt.xlabel("S_rand value", fontsize=18)
    plt.ylabel("Frequency", fontsize=18)    
    plt.hist(numbers, bins=no_bins, color ='green', normed=False)
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)

def generate_tu_entro_distribution(file_in_which_to_save):
    full_entro_dict = pickle.load(open(file_tu_entropies, "rb" ))
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
    plt.xlabel("S_unc value", fontsize=18)
    plt.ylabel("Frequency", fontsize=18)    
    plt.hist(numbers, bins=no_bins, color ='red', normed=False)
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)
    
def gen_overlay_histo(file_in_which_to_save):


    x = pickle.load(open(file_full_entropies, "rb" ))
    y = pickle.load(open(file_rand_entropies, "rb" ))
    z = pickle.load(open(file_tu_entropies, "rb" ))
    numbersx = []
    numbersy =[]
    numbersz = []

    for key in x.keys():
        numbersx.append(round(x[key],2))
    unique_numbersx = []
    for x in numbersx:
        if x not in unique_numbersx:
            unique_numbersx.append(x)
    no_binsx = len(unique_numbersx)

    for key in y.keys():
        numbersy.append(round(y[key],2))
    unique_numbersy = []
    for y in numbersy:
        if y not in unique_numbersy:
            unique_numbersy.append(y)
    no_binsy = len(unique_numbersy)

    for key in z.keys():
        numbersz.append(round(z[key],2))
    unique_numbersz = []
    for z in numbersz:
        if z not in unique_numbersz:
            unique_numbersz.append(z)
    no_binsz = len(unique_numbersz)
        
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)  
    #plt.title("Gaussian Histogram")
    plt.xlabel("Entropy value", fontsize=18)
    plt.ylabel("Frequency", fontsize=18)    

    plt.hist(numbersx, no_binsx, alpha=0.3, label='S')
    plt.hist(numbersy, no_binsy, alpha=0.3, label='S_rand')
    plt.hist(numbersz, no_binsz, alpha=0.3, label='S_unc')
    plt.legend(loc='upper right')

    """p, x = np.histogram(numbersx, bins=no_binsx) # bin it into n = N/10 bins
    x = x[:-1] + (x[1] - x[0])/2   # convert bin edges to centers
    f = UnivariateSpline(x, p, s=len(numbersx))
    plt.plot(x, f(x))
    plt.show()"""    
    
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)


def generate_conditioned_entro_graphic(file_in_which_to_save):
    all_cond_entro = pickle.load(open(file_cond_entropies, "rb" ))
    
    numbers = []
    order = []
    crt = 1
    for key in all_cond_entro.keys():
        for i in all_cond_entro[key]:
            if crt<31:
                numbers.append(all_cond_entro[key][i])
                order.append(crt)
                crt= crt + 1
            else:
                break
        break
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)  
    #plt.title("Gaussian Histogram")
    plt.xlabel("Number of previously known positions", fontsize=18)
    plt.ylabel("S_cond value ", fontsize=18)    

    plt.plot(order, numbers, 'yo-')
    
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)
    
def generate_averages():
    x = pickle.load(open(file_full_entropies, "rb" ))
    y = pickle.load(open(file_rand_entropies, "rb" ))
    z = pickle.load(open(file_tu_entropies, "rb" ))
    t = pickle.load(open(file_pred, "rb"))
    numbersx = []
    numbersy =[]
    numbersz = []
    numberst = []
    for key in x.keys():
        numbersx.append(x[key])

    for key in y.keys():
        numbersy.append(y[key])

    for key in z.keys():
        numbersz.append(z[key])
        
    for key in t.keys():
        numberst.append(t[key])            

    sumx = 0 
    for key in x.keys():
        sumx = sumx + x[key]
    
    avg_x = (sumx+0.0000)/len(numbersx)
    print("Avg entr: ",avg_x)
    
    sumy = 0
    for key in y.keys():
        sumy = sumy + y[key]
    
    avg_y = (sumy+0.0000)/len(numbersy)
    print("Avg entr: ",avg_y)

    sumz = 0
    for key in z.keys():
        sumz = sumz + z[key]
    
    avg_z = (sumz+0.0000)/len(numbersz)
    print("Avg entr: ",avg_z)

    sumt = 0 
    for key in t.keys():
        sumt = sumt + t[key]
    
    avg_t = (sumt+0.0000)/len(numberst)
    print("Pred: ",avg_t)
    
def generate_pred_distribution(file_in_which_to_save):
    users = pickle.load(open(file_pred, "rb" ))
    pred = []
    unique = []
    for key in users:
        pred_val = round(users[key],5)
        pred.append(pred_val-0.005)
        if pred_val not in unique:
            unique.append(pred_val)
        print(key, pred_val)
    
    """"p, x = np.histogram(pred, bins=8) # bin it into n = N/10 bins
    x = x[:-1] + (x[1] - x[0])/2   # convert bin edges to centers
    f = UnivariateSpline(x, p, s=8)
    plt.plot(x, f(x))
    plt.show()"""
    fig = plt.figure()
    fig.clear()
    fig.set_size_inches(15,5)  
    #plt.title("Gaussian Histogram")
    plt.xlabel("Predictability value", fontsize=18)
    plt.ylabel("Frequency", fontsize=18)    

    plt.hist(pred, len(unique), alpha=0.5)
    print(len(unique))
    fig.tight_layout()     
    fig.savefig(file_in_which_to_save)
    
    
    
generate_measurements_and_save_results()
generate_entro_distribution(base+base_entro_pred+"full_entro_distrib.png")
generate_rand_entro_distribution(base+base_entro_pred+"rand_entro_distrib.png")
generate_tu_entro_distribution(base+base_entro_pred+"tu_entro_distrib.png")
gen_overlay_histo(base+base_entro_pred+"overlay.png")
generate_averages()
generate_conditioned_entro_graphic(base+base_entro_pred+"constr.png")
generate_pred_distribution(base+base_entro_pred+"pred_hist.png")
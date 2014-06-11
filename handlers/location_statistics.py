'''
Created on Jun 11, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
from handlers import location_data_handler
import pickle
import os.path
import numpy as np
import matplotlib.pyplot as plt

base = "../../plots/"
#user_list = [4,6,7,11,14,17,19,20]

def prepare_data(user_list):
    """ Creating a dictionary with no of locations for each user as key and value a list with the
    users for which that number has been found"""
    
    location_user_dict = dict()
    
    for user in user_list:
        username = "user_"+str(user)+"_sorted"
        in_file = base+"/"+username+"/"+"star_day_0_step_1_days_30_combined_transitions.p"
        
        loc_over_time_list = location_data_handler.load_pickled_file(in_file)
        #print(loc_over_time_list)
        loc_count = location_data_handler.get_locations_found(loc_over_time_list)
        
        if loc_count in location_user_dict.keys():
            location_user_dict[loc_count].append(user)
        else:
            location_user_dict[loc_count] = []
            location_user_dict[loc_count].append(user)
            
    return location_user_dict

def autolabel(rects,ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')
        
def plot_x_users_y_loc_count(locations_user_dict, file_path):
    """ x - 2 bars - one representing the number of users 
    with the location count equal to the y determining the second bar"""
     
    N = len(locations_user_dict.keys())
    loc_users = []
    for key in locations_user_dict:
        loc_users.append((key,len(locations_user_dict[key]))) # [(loc,no_users),...]
        
    #print(loc_users)
    
    # sort it based on no of locations
    loc_users = sorted(loc_users, key=lambda x: x[0])
    
    #print(loc_users)
    
    locations = []
    user_count = []
    
    for x in loc_users:
        locations.append(x[0])
        user_count.append(x[1])
    
    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, user_count, width, color='r')
    rects2 = ax.bar(ind+width, locations, width, color='b')
    
    # add some information 
    ax.set_ylabel('Count')
    ax.set_title('Number of users with the same number of locations visited over a month')
    ax.set_xticks(ind+width)
    labels_list = []
    for i in range(0,N):
        labels_list.append("G"+str(i+1))
    ax.set_xticklabels( labels_list )

    autolabel(rects1,ax)
    autolabel(rects2,ax)
    
    ax.legend( (rects1[0], rects2[0]), ('Users', 'Locations') )  
    
    fig.savefig(file_path)

def average_number_of_locations(user_list):
    no_users = len(user_list)
    
    result = 0
    
    for user in user_list:
        username = "user_"+str(user)+"_sorted"
        in_file = base+"/"+username+"/"+"star_day_0_step_1_days_30_combined_transitions.p"
        
        loc_over_time_list = location_data_handler.load_pickled_file(in_file)
        
        max_loc = location_data_handler.get_locations_found(loc_over_time_list)
        
        result = result + max_loc

    return result/(no_users+0.0)
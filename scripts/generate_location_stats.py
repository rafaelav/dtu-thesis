'''
Created on Jun 11, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import location_statistics

base = "../../plots/_general_plots/"
user_list = [4,6,7,11,14,17,19,20,24,25,27]

# get locations information from user list
loc_users_dict = location_statistics.prepare_data(user_list)
print(loc_users_dict)

# plot statistics
fig_file = "users_locations_double_bars.png"
location_statistics.plot_x_users_y_loc_count(loc_users_dict, base+fig_file)

# calculate and print average locations per user
print("Average locations per user: "+str(location_statistics.average_number_of_locations(user_list)))
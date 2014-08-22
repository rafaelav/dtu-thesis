'''
Created on Aug 22, 2014

@author: rafa
'''
'''
Created on May 18, 2014

@author: rafa
'''
import datetime
import sys
sys.path.append( ".." )

from handlers import match_handler
from handlers import user_data_handler
from handlers import location_data_handler

user_list = [6]#[4,6,7,11,12,14,17,19,20,24,25,27,32,34,35,36,37,38,39,40,41,44,45,46,48,49,50,52,53,55,57,58,59,60,62,70,72,74,75]
start_day = 0
days_to_consider = 3 # in total
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5
iterations = 10 # number of times it runs hmm before trying to figure out best estimation
step = 1 # number of days to consider in one interval
threshold = 0.80
file_name = "/star_day_0_step_1_days_3_combined_transitions.p"
base = "../../plots/"
def get_marker_for_unknown(user):
    username = "user_"+str(user)+"_sorted"
    unknown_marker = -1
    markers = dict()
    day = 1
    pos = 288
    #while unknown_marker == -1 and day <30:
    
    day_matrix_file="/day_"+str(day)+"_count_1_pickled_presence_matrix.p"
    matrix = location_data_handler.load_pickled_file(base+username+day_matrix_file)
    #print(matrix)
    matrix_keys = matrix.keys()
    locations_file = base+username+file_name
    transitions = location_data_handler.load_pickled_file(locations_file)
    #print(transitions)
    for i in range(0,288):
        found = False
        for key in matrix_keys:
            if matrix[key][i]!=0:
                found = True
                break
        if found == False: # found a position for which all APs are 0
            if transitions[pos + i] in markers.keys():
                #print("pos marker",transitions[pos + i],pos+i)
                markers[transitions[pos + i]] = markers[transitions[pos + i]] + 1
            else:
                #print("pos marker",transitions[pos + i],pos+i) 
                markers[transitions[pos + i]] = 1
        
    maxim = -1        
    for key in markers.keys():
        if markers[key] > maxim:
            unknown_marker = key
            
    print(unknown_marker)        
    return unknown_marker

for user in user_list:
    user_file = "user_"+str(user)+"_sorted"
    # generate transition files for given days
    
    start_moment = datetime.datetime.now()
     
    print("Creating transitions for ",user_file)
    #match_handler.calculate_transitions_over_time(user_file, start_day, days_to_consider, step, m_most_popular_bssids, time_bin, plot_interval, iterations, min_loc, max_loc)
    #end_transitions = datetime.datetime.now()
        
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

    print(combined_locations)
    print(max(combined_locations))
    
    marker_for_unknown = get_marker_for_unknown(user)
    print("unknown",marker_for_unknown)

    user_data = user_data_handler.retrieve_data_from_user(user_file,0,3)    
    start_time = user_data[0][1]
    DAY_INTERVAL_SECS = 24 * 60 * 60
    end_time = end_time = start_time + 3 * DAY_INTERVAL_SECS
        # get colors for the locations (0 to estimated_hidden_states)
    locations = []
    for i in range(0,max(combined_locations)+1):
        locations.append(i)
    colors_dict = user_data_handler.generate_color_codes_for_bssid(locations)
    colors_dict[marker_for_unknown] = '#FFFFFF'
            
    # file path where to plot
    file_path = "../../plots/"+user_file+"/"+"testing_3_day_from_30_matched_locations_2.png"
    # plot transitions
    location_data_handler.plot_locations(combined_locations[0:288*3], 3, 5, user_file, colors_dict, start_time, end_time, 60*3, "k-means",file_path)
    
    print("Start time: "+str(start_moment))
    print("End time creating transitions: "+str(datetime.datetime.now()))
    print("End time creating associations: "+str(datetime.datetime.now()))
    print("End time creating combinations: "+str(datetime.datetime.now()))
    # plot
#     user_data = user_data_handler.retrieve_data_from_user(user_file,start_day,days_to_consider)    
#     start_time = user_data[0][1]
#     end_time = user_data[len(user_data)-1][1]
    #NOT WORKINGmatch_handler.plot_combined_transitions(user_file, time_bin, start_day, days_to_consider, step, plot_interval, start_time,end_time)
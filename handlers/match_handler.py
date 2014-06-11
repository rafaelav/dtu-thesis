'''
Created on May 18, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )
from handlers import user_data_handler
from handlers import location_data_handler
import pickle
import os.path

# using K-fold cross validation is used
K = 10
# final variable
base = "../../plots/"
LOC_TYPE = "hmm"
DAY_INTERVAL_SECS = 24 * 60 * 60

def calculate_transitions_over_time(user_file, start_day, days_count, step, m_most_popular_bssids, time_bin, plot_interval, iterations, min_loc, max_loc):
    days_to_consider = step # always process step days at the time
    start_days = []
    for day in range(start_day, start_day+days_count,step):
        start_days.append(day)
        print(day)
        # create the transition matrix for each day
        transitions, estimated_hidden_states, start_time, end_time = create_transition_array(user_file, day, days_to_consider, m_most_popular_bssids, time_bin, iterations, min_loc, max_loc)
        save_transitions(user_file, day, days_to_consider, transitions)
        file_path = "../../plots/"+user_file+"/"+"hmm_locations_"+"day_"+str(day)+"_count_"+str(days_to_consider)+"_plot.png"
        plot_transitions(user_file, days_to_consider, estimated_hidden_states, transitions, time_bin, start_time, end_time, plot_interval, file_path)
    print(start_days)
        
def save_transitions(user_file, day, days_to_consider, transitions):
    transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(days_to_consider)+"_transitions.p"
    
    # save transitions for currentd day
    pickle.dump(transitions, open(transitions_file, "wb"))    

def save_combined_transitions(user_file, start_day, days_to_consider, step, combined_transitions):
    combined_transitions_file = base+user_file+"/"+"star_day_"+str(start_day)+"_step_"+str(step)+"_days_"+str(days_to_consider)+"_combined_transitions.p"
    
    # save transitions for currentd day
    pickle.dump(combined_transitions, open(combined_transitions_file, "wb"))    
        
def create_transition_array(user_file, day, days_to_consider, m_most_popular_bssids,time_bin, iterations, min_loc, max_loc):
    pickled_matrix_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(days_to_consider)+"_pickled_presence_matrix.p"

    user_data = user_data_handler.retrieve_data_from_user(user_file,day,days_to_consider)    
    start_time = user_data[0][1]
    #end_time = user_data[len(user_data)-1][1]
    end_time = start_time + days_to_consider * DAY_INTERVAL_SECS
    
    # only re-calculate presence matrxi and pickle it if it doens't already exist
    if not os.path.isfile(pickled_matrix_file):
        print("Matrix was not claculated previously... need to do this now")
        # make presence matrix
        pickle_presence_matrix(user_file, day, days_to_consider, time_bin, m_most_popular_bssids)
        print("Matrix calculation is complete")
    
    # load matrix
    presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)
    
    # make presence matrix for hmm
    hmm_matrix, bssids = location_data_handler.create_matrix_for_hmm(presence_matrix)
    
    # determine locations estimation
    dict_estimations = dict()
    for iter in range(0,iterations):
        print("ITERRATION: "+str(iter+1)+"/"+str(iterations))
        estimated_hidden_states, transitions_between_states = location_data_handler.estimate_locations_k_fold_cross_validation(K, hmm_matrix, min_loc, max_loc, LOC_TYPE)
        if estimated_hidden_states not in dict_estimations.keys(): # this number was never estimated before
            dict_estimations[estimated_hidden_states] = []
        dict_estimations[estimated_hidden_states].append(transitions_between_states) # add solution for this estimations
    
    # find most likely estimate and pick a transition
    max = 0
    states = 0
    for key in dict_estimations.keys():
        if len(dict_estimations[key])>max:
            max = len(dict_estimations[key])
            states = key
    
    estimated_hidden_states = states # get the best posibility
    transitions_between_states = dict_estimations[estimated_hidden_states][0] # take fist transitions it estimated for given states 

#     print("DAY "+str(day)+" COUNT "+str(days_to_consider)+" - Results (estimated number of locations and transitions between them")
#     print(estimated_hidden_states)
#     print(transitions_between_states)
    return transitions_between_states, estimated_hidden_states, start_time, end_time

def plot_transitions(user_file, days_to_consider, estimated_hidden_states, transitions, time_bin, start_time, end_time, plot_interval, file_path):
    # get colors for the locations (0 to estimated_hidden_states)
    locations = []
    for i in range(0,estimated_hidden_states):
        locations.append(i)
    colors_dict = user_data_handler.generate_color_codes_for_bssid(locations)
        
    # plot transitions
    location_data_handler.plot_locations(transitions, days_to_consider, time_bin, user_file, colors_dict, start_time, end_time, plot_interval*days_to_consider, LOC_TYPE, file_path)


def pickle_presence_matrix(user_file, start_day, days_to_consider, time_bin, m_most_popular_bssids):
    ### Prepare and calculate pickled matrix for m_most_popolar
    # prepare needed data
    user_data, start_time, end_time, bssid_times_and_rssis_dict = location_data_handler.prepare_data(user_file, start_day, days_to_consider, m_most_popular_bssids)
    # get matrix
    presence_on_rows, column_elements =  location_data_handler.get_bssid_presence_matrix(start_time, end_time, bssid_times_and_rssis_dict, time_bin)

    print("Number of bssids in matrix:",len(presence_on_rows.keys()))
    print("Need to pickle")
    if m_most_popular_bssids == -1:
        pickle.dump(presence_on_rows, open("../../plots/"+user_file+"/"+"day_"+str(start_day)+"_count_"+str(days_to_consider)+"_pickled_presence_matrix.p", "wb"))
    else:
        print("NOT TRATING CASE WITH LESS BSSIDS")
    print("Pickled")
    
def extract_fingerprints_for_locations(transitions_file, presence_matrix_file, day):
    """ For each location we look for each bssid at their presence during the times
    that location has been spotted. If mostly a bssid is spotted during that time 
    with presence value 0 then we consider that the final fingerprint for the 
    location should have value eaqual to 0 for that bssid. The same for value 1.
    """
    presence_matrix = location_data_handler.load_pickled_file(presence_matrix_file)
    transitions = location_data_handler.load_pickled_file(transitions_file)
    
    bssids = presence_matrix.keys()
    
    print("DAY - "+str(day))
    print(presence_matrix.keys())
    print(len(presence_matrix[bssids[0]]))
    print(len(transitions),transitions)
    
    # fingerprint[i] - shows fingerprint of locations i. It is presented ad dictionary of bssids with 0 or 1
    fingerprints = []
    # predominance[i][bssid] = [m, n] - for location i for bssid keeps number (m) of 0 values and number (n) of 1 values encountered
    predominance = []
    for i in range(0,max(transitions)+1):
        newfdict = dict()
        fingerprints.append(newfdict)
        for bssid in bssids:
            fingerprints[i][bssid] = -1

        newpdict = dict()
        predominance.append(newpdict)
        for bssid in bssids:
            predominance[i][bssid] = [0, 0] # initially 0 encounters for both 1 and 0
    
    for bin in range(0,len(transitions)):
        for bssid in bssids:
            #            location          bssid  value 0 or 1 at pos bin in pres matrix for bssid
            predominance[transitions[bin]][bssid][presence_matrix[bssid][bin]] = predominance[transitions[bin]][bssid][presence_matrix[bssid][bin]] + 1
            
    for x in range(0, max(transitions)+1):
        for bssid in bssids:
            if predominance[x][bssid][0]>predominance[x][bssid][1]:
                fingerprints[x][bssid] = 0
            else:
                fingerprints[x][bssid] = 1
        print("LOCATION "+str(x))
        print(fingerprints[x])
    return fingerprints

def start_association_dictionary(fingerprints):
    next_location = len(fingerprints)
    print(next_location)
    
    association = []
    for loc in range(0,len(fingerprints)):
        association.append((loc, fingerprints[loc])) # location name (e.g. 0), fingerprint for location
    print("will return",association)
    return next_location,association

def add_to_assiciation_dictionary(fingerprints, next_location, previos_associations, crt_day, start_day, threshold):
    """ Looks in associations from previous days and sees if there is anything that 
    matchs the current fingerprints for the current day. In case there is, than the
    current fingerprint's location is the same as the one it matched from previous days.
    In case it doesn't find anything then it attributes it a new location
    """
    THR = threshold
    association = []
    # for each location in crt day (and its fingerprint)
    for loc in range(0,len(fingerprints)):
        found = False
        # we look in all previous days
        for prev_day in range(start_day, crt_day):
            # for fingerprints of locations
            for element in previos_associations[prev_day]:
                # and calculate the similarty 
                similarity = get_similarity_common_bssids_and_active_bssid(element[1],fingerprints[loc]) # fingerprint of previous location and fingerprint of location in crt day
                # if the similarity is above a threshold 
                if similarity >= THR:
                    found = True # we said we found something similar
                    association.append((element[0], fingerprints[loc])) # associate to this location in day crt_day the name of the location in similar element and remember the fingerprint 
                    break
            if found == True:
                break
        # if we didn't find anything in any previous days it means it's a new type of location
        if found == False:
            association.append((next_location, fingerprints[loc])) # we remember it 
            next_location = next_location + 1 # we increase the next_location seens this was ussed
    if len(association)!= len(fingerprints):
        print("ERROR - NOT ALL LOCATIONS HAVE ASSOCIATIONS")
    return next_location, association

# NOT USED
def get_similarity_divided_to_common_bssids(dict_a, dict_b):
    """ There's a A-B similarity calculated that means the number of bssids in A that exist
    in B and have the same presence value attributed divided to the number of common bssids between A and B.
    There is a similar B-A similarity. The overall similarity is calculated as the sum of the 
    two previously mentioned values divided to 2.
    """
    similarity_ab = 0
    common_ab = 0
    for key in dict_a:
        if key in dict_b: # bssid in both dictionaries
            print(key, dict_a[key], dict_b[key])
            common_ab = common_ab + 1
            if dict_a[key]==dict_b[key]: # and the key is the same
                similarity_ab = similarity_ab + 1 # we increment similarity 
    #similarity_ab = (similarity_ab + 0.0) / len(dict_a.keys())
    similarity_ab = (similarity_ab + 0.0) / common_ab
    print("ab",similarity_ab)

    similarity_ba = 0
    common_ba = 0
    for key in dict_b:
        if key in dict_a: # bssid in both dictionaries
            common_ba = common_ba + 1
            if dict_a[key]==dict_b[key]: # and the key is the same
                similarity_ba = similarity_ba + 1 # we increment similarity 
    #similarity_ba = (similarity_ba + 0.0) / len(dict_b.keys())
    similarity_ba = (similarity_ba + 0.0) / common_ba
    print("ba",similarity_ba)
    
    similarity = (similarity_ab + similarity_ba)/2.0
    print("sim",similarity)
    
    return similarity

#NOT USED
def get_similarity_reunion_bssids(dict_a, dict_b):
    """A reunion for bssids from both A and B is calculated. In case a bssid is not in A or B but it is 
    in the reunion, than the presence value attributed for it is 0. In case a bssid is in A or B and
    the value for it in the original dictionary was 1, then it stays 1. The similarity is calculated as
    the number of bssids that have the same value for both the new dictionaries for A and B, divided to
    the number of bssids in either of these dictionaries (it's the same number since it's the reunion) 
    """
    dict_a_modified = dict()
    dict_b_modified = dict()
    #print("A,B",len(dict_a.keys()),len(dict_b.keys()))
    
    for key in dict_a:
        if key not in dict_a_modified:
            dict_a_modified[key] = 0
        if key not in dict_b_modified:
            dict_b_modified[key] = 0

    for key in dict_b:
        if key not in dict_a_modified:
            dict_a_modified[key] = 0
        if key not in dict_b_modified:
            dict_b_modified[key] = 0
                
    for key in dict_a:
        if dict_a[key] == 1:
            dict_a_modified[key] = 1

    for key in dict_b:
        if dict_b[key] == 1:
            dict_b_modified[key] = 1
    
#     print(len(dict_a_modified.keys()), len(dict_b_modified.keys()))
#     for key in dict_a_modified:
#         if key not in dict_b_modified:
#             print("ERROR")
#     for key in dict_b_modified:
#         if key not in dict_a_modified:
#             print("ERROR")                              
                                          
    similarity = 0
    for key in dict_a_modified:
        if dict_a_modified[key]==dict_b_modified[key]: # and the key is the same
            similarity = similarity + 1 # we increment similarity 
    similarity = (similarity + 0.0) / len(dict_a_modified.keys())
        
    return similarity

def get_similarity_common_bssids_and_active_bssid(dict_a, dict_b):
    """
    A reunion of only the bssids that are 1 in either a or b and the bssids that exist in both a and b 
    (can also be 0) is calculated. The similarity is calculated as the number of bssids in this reunion 
    that have the same presence associated for both a and b divided to the total number of these bssids 
    (same in a and b).
    """
    # if all keys in a and b have 0 associated to it then they are the NONE location
    onlyZeros = True
    for key in dict_a:
        if dict_a[key] == 1:
            onlyZeros = False

    for key in dict_b:
        if dict_b[key] == 1:
            onlyZeros = False
    if onlyZeros == True:
        return 1
    
    # else
    dict_a_modified = dict()
    dict_b_modified = dict()
    #print("A,B",len(dict_a.keys()),len(dict_b.keys()))
    
    for key in dict_a:
        if dict_a[key] == 1:            
            dict_a_modified[key] = 1
            if key in dict_b:
                dict_b_modified[key] = dict_b[key]
            else:
                dict_b_modified[key] = 0
        else:
            if key in dict_b:
                dict_a_modified[key] = 0
                dict_b_modified[key] = dict_b[key]

    for key in dict_b:
        if key not in dict_b_modified:
            if dict_b[key] == 1:            
                dict_b_modified[key] = 1
                if key in dict_a:
                    dict_a_modified[key] = dict_a[key]
                else:
                    dict_a_modified[key] = 0
            else:
                if key in dict_a:
                    dict_b_modified[key] = 0
                    dict_a_modified[key] = dict_a[key]
                
    if len(dict_a_modified.keys()) != len(dict_b_modified.keys()):
        print("ERROR")
#     print(len(dict_a_modified.keys()), len(dict_b_modified.keys()))
#     for key in dict_a_modified:
#         if key not in dict_b_modified:
#             print("ERROR")
#     for key in dict_b_modified:
#         if key not in dict_a_modified:
#             print("ERROR")                              
                                          
    similarity = 0
    for key in dict_a_modified:
        if dict_a_modified[key]==dict_b_modified[key]: # and the key is the same
            similarity = similarity + 1 # we increment similarity 
    similarity = (similarity + 0.0) / len(dict_a_modified.keys())
        
    return similarity

def make_location_associations(user_file, start_day, days_to_consider, step, threshold):
    """ Creates a dictionary with associations. associations[day]: [(loc,fingerprint),(),()...]
    Each day has associated a list where the ith element in the list is a tuple (a, b), where a is
    the location attributed to location i from given day and b is the fingerprint for that location
    as it has been identified in that day (so even if the location is considered as one which
    has been previously found, the fingerprint is for the location that just has been found) 
    """
    associations = dict()
    for day in range(start_day, start_day+days_to_consider,step):
        newlist = [] 
        #associations.append(newlist)
        associations[day]=newlist
        presence_matrix_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_pickled_presence_matrix.p"
        transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_transitions.p"
    
        fingerprints = extract_fingerprints_for_locations(transitions_file, presence_matrix_file, day)
    
        if day == start_day:
            next_location, associations[day] = start_association_dictionary(fingerprints)
    #        print(associations[day])
            continue
        
        next_location, associations[day] = add_to_assiciation_dictionary(fingerprints, next_location, associations, day, start_day, threshold)
    return associations   

def transform_transitions(transitions, association):
    new_transitions = []
    for bin in range(0,len(transitions)):
        new_transitions.append(association[transitions[bin]][0])
#     for loc in range(0,max(transitions)+1):
#         print(loc,association[loc][0])
#     print("HERE")
#     print("old",transitions)
#     print("new",new_transitions)
    return new_transitions

def combine_locations_with_correct_associations(user_file, start_day, days_to_consider, step, associations):
    new_transitions = dict()
    for day in range(start_day, start_day+days_to_consider,step):
        # extarct original transitions
        transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_transitions.p"
        transitions = location_data_handler.load_pickled_file(transitions_file)
        new_transitions[day] = transform_transitions(transitions, associations[day])
    
    # combining them
    combined_transitions = []
    for day in range(start_day, start_day+days_to_consider,step):
        combined_transitions = combined_transitions + new_transitions[day]
    
    # save it
    save_combined_transitions(user_file, start_day, days_to_consider, step, combined_transitions)
    
    return combined_transitions

# NOT WORKING
def plot_combined_transitions(user_file, time_bin, start_day, days_to_consider, step, plot_interval, start_time,end_time):
    combined_transitions_file = base+user_file+"/"+"start_day_"+str(start_day)+"_step_"+str(step)+"_days_"+str(days_to_consider)+"_combined_transitions.p"
    combined_transitions = location_data_handler.load_pickled_file(combined_transitions_file)
    
    file_path = base+user_file+"/"+"combined_locations_start_day_"+str(start_day)+"_step_"+str(step)+"_days_"+str(days_to_consider)+"_plot.p"
    
    plot_transitions(user_file, days_to_consider, max(combined_transitions)+1, combined_transitions, time_bin, start_time, end_time, plot_interval, file_path)
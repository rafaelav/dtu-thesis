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

user_list = [6]
start_day = 0
days_to_consider = 2 # in total
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5
iterations = 10 # number of times it runs hmm before trying to figure out best estimation
step = 1 # number of days to consider in one interval
day = 0
user_file = "user_6_sorted"

pickled_matrix_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_pickled_presence_matrix.p"
transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_transitions.p"
presence_matrix = location_data_handler.load_pickled_file(pickled_matrix_file)
transitions = location_data_handler.load_pickled_file(transitions_file)
print(presence_matrix.keys())
print(len(presence_matrix[1536]))
print(len(transitions),transitions)


def extract_fingerprints_for_locations(transitions_file, presence_matrix_file, day):
    presence_matrix = location_data_handler.load_pickled_file(presence_matrix_file)
    transitions = location_data_handler.load_pickled_file(transitions_file)
    
    bssids = presence_matrix.keys()
    
#     print("DAY - "+str(day))
#     print(presence_matrix.keys())
#     print(len(presence_matrix[bssids[0]]))
#     print(len(transitions),transitions)
    
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
        
#     print("Predominance for "+str(bssids[0])+" location 0")
#     print(predominance[1][bssids[0]])
#     apps = []
#     for bin in range(0,len(transitions)):
#         if transitions[bin]==1:
#             apps.append(presence_matrix[bssid][bin])
#     print("Original 1,0 markers for "+str(bssids[0])+" location 0")
#     print(apps)
#     print("Fingerprint")
#     print(fingerprints[1][bssids[0]])
    
    return fingerprints

def get_similarity_divided_to_common_bssids(dict_a, dict_b):
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

def get_similarity_reunion_bssids(dict_a, dict_b):
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

def start_association_dictionary(fingerprints):
    next_location = len(fingerprints)
    print(next_location)
    
    association = []
    for loc in range(0,len(fingerprints)):
        association.append((loc, fingerprints[loc])) # location name (e.g. 0), fingerprint for location
    print("will return",association)
    return next_location,association

THR = 0.95
def add_to_assiciation_dictionary(fingerprints, next_location, previos_associations, crt_day, start_day):
    association = []
    # for each location in crt day (and its fingerprint)
    for loc in range(0,len(fingerprints)):
        found = False
        # we look in all previous days
        for prev_day in range(start_day, crt_day):
            # for fingerprints of locations
            for element in previos_associations[prev_day]:
                # and calculate the similarty 
                similarity = get_similarity_reunion_bssids(element[1],fingerprints[loc]) # fingerprint of previous location and fingerprint of location in crt day
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

associations = dict()
next_location = -1
start_day = 0
days_to_consider = 2
for day in range(start_day,days_to_consider):
    newlist = [] 
    #associations.append(newlist)
    associations[day]=newlist
    presence_matrix_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_pickled_presence_matrix.p"
    transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_transitions.p"
    if day == 1:
        trans_1 = location_data_handler.load_pickled_file(transitions_file)

    fingerprints = extract_fingerprints_for_locations(transitions_file, presence_matrix_file, day)

    if day == start_day:
        next_location, associations[day] = start_association_dictionary(fingerprints)
#        print(associations[day])
        continue
    
    next_location, associations[day] = add_to_assiciation_dictionary(fingerprints, next_location, associations, day, start_day)

print(len(associations[0]))
print(len(associations[1]))
crt = 0
for elem in associations[0]:
    print("day 0, location "+str(crt),elem[0])
    crt = crt +1
    
crt = 0
for elem in associations[1]:
    print("day 1, location "+str(crt),elem[0])
    crt = crt +1
    
print(trans_1)

smth = location_data_handler.load_pickled_file(base+user_file+"/"+"day_"+str(0)+"_count_"+str(1)+"_transitions.p")
print("smth",smth)

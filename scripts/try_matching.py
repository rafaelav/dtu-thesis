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

def get_similarity(dict_a, dict_b):
    similarity_ab = 0
    for key in dict_a:
        if key in dict_b: # bssid in both dictionaries
            if dict_a[key]==dict_b[key]: # and the key is the same
                similarity_ab = similarity_ab + 1 # we increment similarity 
    similarity_ab = (similarity_ab + 0.0) / len(dict_a.keys())
    print(similarity_ab)

    similarity_ba = 0
    for key in dict_b:
        if key in dict_a: # bssid in both dictionaries
            if dict_a[key]==dict_b[key]: # and the key is the same
                similarity_ba = similarity_ba + 1 # we increment similarity 
    similarity_ba = (similarity_ba + 0.0) / len(dict_b.keys())
    print(similarity_ba)
    
    similarity = (similarity_ab + similarity_ba)/2.0
    print(similarity)
    
    return similarity

def start_association_dictionary(fingerprints):
    next_location = len(fingerprints)
    print(next_location)
    
    association = []
    for loc in range(0,len(fingerprints)):
        association.append((loc, fingerprints[loc])) # location name (e.g. 0), fingerprint for location
    
    return next_location,association

THR = 0.90
def add_to_assiciation_dictionary(fingerprints, next_location, previos_associations, crt_day):
    association = []
    # for each location in crt day (and its fingerprint)
    for loc in range(0,len(fingerprints)):
        found = False
        # we look in all previous days
        for prev_day in range(0, crt_day):
            # for fingerprints of locations
            for element in previos_associations[prev_day]:
                # and calculate the similarty 
                similarity = get_similarity(element[1],fingerprints[loc]) # fingerprint of previous location and fingerprint of location in crt day
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

associations = []
next_location = -1
for day in range(0,days_to_consider):
    newlist = []
    associations.append(newlist)
    presence_matrix_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_pickled_presence_matrix.p"
    transitions_file = base+user_file+"/"+"day_"+str(day)+"_count_"+str(step)+"_transitions.p"

    fingerprints = extract_fingerprints_for_locations(transitions_file, presence_matrix_file, day)

    if day == 0:
        next_location, associations[day] = start_association_dictionary(fingerprints)
#        print(associations[day])
        continue
    
    next_location, associations[day] = add_to_assiciation_dictionary(fingerprints, next_location, associations, day)

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

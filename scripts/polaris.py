'''
Created on Feb 11, 2014

@author: rafa
'''
import math

"""def get_fingerprint_aprox_similarity(fp_a, fp_b):
    common = count_common_bssids(fp_a, fp_b)
    return 2*common"""

def get_signal_level(rssi):
    """ Calculates signal level based on rssi"""
    lvl = 9 - math.ceil(math.fabs(rssi+59)/5.0)
    return lvl

def get_signal_similarity(rssi_a, rssi_b):
    """ Determines if the signal strength of 2 bssids is similar (both are strong or not) - it takes into consideration both the number difference as well as the signal power"""
    lvl_a = get_signal_level(rssi_a)
    lvl_b = get_signal_level(rssi_b)
    
    # normalized to be between [0,1]
    sig_sim = 1 - math.fabs(math.pow(2,lvl_a)-math.pow(2, lvl_b))/(math.pow(2, 8)+0.0)
    
    return sig_sim

def count_common_bssids(fp_a, fp_b):
    count = 0
    for x in fp_a:
        for y in fp_b:
            if x[0] == y[0]:  # same bssid
                count = count + 1
                break
    return count

def get_fingerprint_similarity(fp_a, fp_b):
    sim = 0
    
    common = count_common_bssids(fp_a, fp_b)
    
    if common == 0:
        print("Nothing common")
        print(fp_a)
        print(fp_b)
        return sim
        
    for x in fp_a:
        for y in fp_b:
            if x[0] == y[0]:  # same bssid
                sig_sim = get_signal_similarity(x[1],y[1])
                sim = sim + sig_sim
                break   # can move to next bssid since it will not be repeted
    
    sim = sim / (common+0.0) # normalize it between [0,1]
    return sim
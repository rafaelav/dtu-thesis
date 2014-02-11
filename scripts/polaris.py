'''
Created on Feb 11, 2014

@author: rafa
'''
import math

def get_signal_level(rssi):
    lvl = 9 - math.ceil(math.fabs(rssi+59)/5.0)
    return lvl

def get_signal_similarity(rssi_a, rssi_b):
    lvl_a = get_signal_level(rssi_a)
    lvl_b = get_signal_level(rssi_b)
    
    # normalized to be between [0,1]
    sig_sim = 1 - math.fabs(math.pow(2,lvl_a)-math.pow(2, lvl_b))/(math.pow(2, 8)+0.0)
    
    return sig_sim

def count_common_bssids(fp_a, fp_b):
    count = 0
    for (x,y) in fp_a:
        for (z,t) in fp_b:
            if x == z:  # same bssid
                count = count + 1
                break
    return count

def get_fingerprint_similarity(fp_a, fp_b):
    sim = 0
    for (x,y) in fp_a:
        for (z,t) in fp_b:
            if x == z:  # same bssid
                sig_sim = get_signal_similarity(y,t)
                sim = sim + sig_sim
                break   # can move to next bssid since it will not be repeted
    common = count_common_bssids(fp_a, fp_b)
    sim = sim / (common+0.0) # normalize it between [0,1]
    return sim

def get_fingerprint_aprox_similarity(fp_a, fp_b):
    common = count_common_bssids(fp_a, fp_b)
    return 2*common
'''
Created on Feb 10, 2014

@author: rafa
'''

class AccessPoint(object):
    '''
    classdocs: Contains the bssid (identity of AP) and rssi (signal strength of AP). 
    '''

    def __init__(self, bssid, rssi):
        '''
        Constructor
        '''
        self.bssid = bssid
        self.rssi = rssi
        
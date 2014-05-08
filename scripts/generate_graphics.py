'''
Created on May 8, 2014

@author: rafa
'''
import sys
sys.path.append( ".." )

from graphics import plot_bssid_presence
from graphics import plot_hmm_locations
from graphics import plot_bssid_rssi
user_list = [1,2,3,6,9,15,17,18,40]
start_day = 0
days_to_consider = 1
n_best_signal_bssids = -1 
m_most_popular_bssids = -1
max_in_legend = 10
days_count = 1
plot_interval = 60 # per ne day plot xticks are from 60 to 60 mins
time_bin = 5

# ploting signal strength for bssids over time
plot_bssid_rssi.start_plot_bssid_rssi(user_list, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, max_in_legend, days_count, plot_interval)
plot_bssid_presence.start_plot_presence(user_list, start_day, days_to_consider, n_best_signal_bssids, m_most_popular_bssids, time_bin, plot_interval)
plot_hmm_locations.start_plot_hmm_locations(user_list, start_day, days_to_consider, m_most_popular_bssids, time_bin, plot_interval)

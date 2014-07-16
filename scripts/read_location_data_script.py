'''
Created on Jul 15, 2014

@author: rafa
'''
import io

def read_location_data(user_file_name):
    user_data = []
    print('../../location_data/{0}'.format(user_file_name))
    crt = 0
    with io.open('../../location_data/{0}'.format(user_file_name), encoding='utf-8') as f:
        for line in f:
            split_line = line.split()
            print(split_line)
            crt = crt + 1
            if crt == 10:
                break
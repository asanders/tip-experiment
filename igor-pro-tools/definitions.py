# dictionary of computer name to data folder locations
data_locs = {}
data_locs['ALAN-VAIO'] = 'C:\\Users\\Alan\\SkyDrive\\Documents\\work\\'\
                         '0 - experiment\\data\\raw data'
data_locs['NP-ASTATINE'] = 'C:\\Users\\Alan\\Documents\\0 - experiment\\'\
                           'data\\raw data'
data_locs['NP-MAGNESIUM'] = 'C:\\Users\\Hera\\Desktop\\tip_exp\\raw_data'

import os

def get_host_name():
    return os.getenv('computername')

def get_host_data_folder():
    name = os.getenv('computername')
    return data_locs[name]

if __name__ == '__main__':
    print get_host_name()
    print get_host_data_folder()

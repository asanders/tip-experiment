"""
Batch tip alignment displays
"""

import os
import sys
file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
root_dir = os.path.dirname(file_dir)

# load computer definitions and data handling #
module_dir = os.path.join(root_dir, "igor-pro-tools")
if module_dir not in sys.path:
	sys.path.append(module_dir)
from definitions import *
from import_igor_txt_data import *
from data_handling import *

from resonance_scan_display import *
from tip_alignment_display import *
from tip_experiment_display import *
from tip_alignment_analysis import *

# user prompts #
data_path = get_host_data_folder()
mon_yr = raw_input("Enter month_year (mon_yyyy): ")
day = raw_input("Enter day (dd): ")

# set day folder
init_path = os.path.join(data_path, str(mon_yr))
init_path = os.path.join(init_path, "day_" + str(day))

# resonance scans #
if os.path.exists(os.path.join(init_path, 'resonance_scans')):
    print '\nResonance Scans:'
    path = os.path.join(init_path, 'resonance_scans')
    scans = [os.path.join(path, x) for x in os.listdir(path)
             if os.path.isdir(os.path.join(path, x)) and 'scan_' in x]
    for scan in scans:
        print os.path.basename(scan)
        display_resonance_scan(scan)

# alignment scans #
if os.path.exists(os.path.join(init_path, 'alignment_scans')):
    print '\nAlignment Scans:'
    path = os.path.join(init_path, 'alignment_scans')
    scans = [os.path.join(path, x) for x in os.listdir(path)
             if os.path.isdir(os.path.join(path, x)) and 'scan_' in x]
    sets = []
    for scan in scans:
        display_alignment_scan(scan)
        # load parameters for scan and extract alignment set #
        wparams = load_2d_txt_data(os.path.join(scan, "parameters.itx"))
        params = {}
        for x in wparams:
            if x[0] == 'time_stamp':
                params[x[0]] = x[1]
            elif x[0] == 'alignment_set':
                params[x[0]] = int(x[1])
            else:
                params[x[0]] = float(x[1])
        try:
            alignment_set = params['alignment_set']
        except KeyError:
            alignment_set = 0
        if alignment_set not in sets:
            sets.append(alignment_set)

    # alignment set analysis #
    for alignment_set in sets:
        analyse_alignment_data(path, alignment_set)
        
        

# tip experiment scans #
path = init_path
scans = [os.path.join(path, x) for x in os.listdir(path)
         if os.path.isdir(os.path.join(path, x)) and "tip_exp_" in x]
for scan in scans:
    #print os.path.basename(scan)
    display_experiment_scan(scan)

os.system("pause")

import os
import sys
file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
version_dir = os.path.dirname(file_dir)
root_dir = os.path.dirname(version_dir)
# load computer definitions and data handling #
module_dir = os.path.join(root_dir, "igor-pro-tools")
if module_dir not in sys.path:
	sys.path.append(module_dir)
from definitions import *
from data_classes import *
from figure_classes import *
import matplotlib.pyplot as plt

def display_tip_experiment_scan(location):
    data = spatial_data(location)
    figure = spatial_figure(data)
    
    # check for any time-resolved measurements to plot #
    time_res_data_path = os.path.join(location, "time_resolved_data")
    time_res_scans = [(x.rsplit("_", 1)[1]).split(".",1)[0]
                       for x in os.listdir(time_res_data_path)
                       if "qc_spec" in x and ".ibw" in x
                       and "timing" not in x and "wavelength" not in x]
    for instance in time_res_scans:
        data = temporal_data(location, instance)
        figure = temporal_figure(data)
    return 0

if __name__ == "__main__":
    init_target = get_host_data_folder()
    mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    day = raw_input("Enter day (dd): ")
    scan_n = raw_input("Enter scan: ")
    target = os.path.join(init_target, str(mon_yr))
    target = os.path.join(target, "day_" + str(day))
    target = os.path.join(target, "tip_exp_" + str(scan_n))
    display_tip_experiment_scan(target)
    plt.show()
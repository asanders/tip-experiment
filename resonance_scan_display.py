"""
Plots tip alignment data in a more useful display.
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

from igor.binarywave import load as loadibw
import numpy as np
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc
import matplotlib.gridspec as gridspec
from scipy import ndimage
from mpl_toolkits.mplot3d import proj3d

def add_res_subplot(mag, phase, frequency, name, fig, ax, formatter):    
    ax = fig.add_subplot(ax)
    ax.plot(frequency, mag, 'k-')
    ax2 = ax.twinx()
    ax2.plot(frequency, phase, 'k--')

    ax.xaxis.set_major_formatter(formatter) 
    ax.yaxis.set_major_formatter(formatter)
    
    ax.set_xlabel('frequency (Hz)')
    if name == 'electronic':
        ax.set_ylabel('magnitude (A)')
    elif name == 'force':
        ax.set_ylabel('magnitude (V)')
    ax2.set_ylabel('phase ($\degree$)')
    ax.text(0.03, 0.97, name, ha='left', va='top', color='black',
            fontsize=11, fontweight='bold', transform=ax.transAxes)
    return 0

def display_resonance_scan(target):
    # load parameters inforamtion
    params = load_params(target)

    # extract resonance data - requires fixing
    scan_n = int(os.path.basename(target).rsplit("_", 1)[1])
    #scan_size = params['scan_size']
    #scan_step = params['scan_step']
    #frequency = params['frequency']
    #voltage = params['voltage']
    #offset = params['offset']
    #init_pos_a = params['init_pos_a']
    #init_pos_b = params['init_pos_b']
    #init_pos_c = params['init_pos_c']
    #time_stamp = params['time_stamp']
    try:
        electronic_alignment = params['electronic_alignment']
    except KeyError:
        electronic_alignment = 1
    try:
        force_alignment = params['force_alignment']
    except KeyError:
        force_alignment = 0

    # load required data
    frequency = loadibw(os.path.join(target, "frequency.ibw"))
    frequency = frequency['wave']['wData']
    frequency = frequency.T
    if electronic_alignment == 1:
        res_scan_r = loadibw(os.path.join(target, "resonance_scan_r.ibw"))
        res_scan_r = res_scan_r['wave']['wData']
        res_scan_r = res_scan_r.T
        res_scan_theta = loadibw(os.path.join(target, "resonance_scan_theta.ibw"))
        res_scan_theta = res_scan_theta['wave']['wData']
        res_scan_theta = res_scan_theta.T
    if force_alignment == 1:
        res_scan_fr = loadibw(os.path.join(target, "resonance_scan_fr.ibw"))
        res_scan_fr = res_scan_fr['wave']['wData']
        res_scan_fr = res_scan_fr.T
        res_scan_ftheta = loadibw(os.path.join(target, "resonance_scan_ftheta.ibw"))
        res_scan_ftheta = res_scan_ftheta['wave']['wData']
        res_scan_ftheta = res_scan_ftheta.T

    # Set up the figure
    fig_width_cm = 15.0
    inches_per_cm = 1.0/2.54
    fig_width = fig_width_cm * inches_per_cm
    golden_mean = (np.sqrt(5)-1.0)/2.0
    if force_alignment == 1:
        multi = 2
    else:
        multi = 1
    fig_height = 1.2 * multi * golden_mean * fig_width
    fig_size = (fig_width, fig_height)
    params = {'backend': 'ps',
              'axes.labelsize': 11,
              'text.fontsize': 11,
              'legend.fontsize': 11,
              'xtick.labelsize': 11,
              'ytick.labelsize': 11,
              'text.usetex': False,
              'figure.subplot.left' : 0.01,
              'figure.subplot.bottom' : 0.01,
              'figure.subplot.right' : 0.99,
              'figure.subplot.top' : 0.99,
              'figure.subplot.wspace' : 0.02,
              'figure.subplot.hspace' : 0.02,
              'figure.figsize': fig_size}
    plt.rcParams.update(params)

    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))

    plt.close('all')
    fig = plt.figure()
    if electronic_alignment == 1 and force_alignment == 0:
        gs0 = gridspec.GridSpec(1, 2, width_ratios=[1,0.2])    
        #gs00 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec=gs0[5])
        electronic_ax = plt.Subplot(fig, gs0[0, 0])
        # subplots
        add_res_subplot(res_scan_r, res_scan_theta, frequency, "electronic", fig, electronic_ax, formatter)
    elif electronic_alignment == 1 and force_alignment == 1:
        gs0 = gridspec.GridSpec(2, 2, width_ratios=[1,0.2])
        electronic_ax = plt.Subplot(fig, gs0[0, 0])
        force_ax = plt.Subplot(fig, gs0[1, 0])
        # subplots
        add_res_subplot(res_scan_r, res_scan_theta, frequency, "electronic", fig, electronic_ax, formatter)
        add_res_subplot(res_scan_fr, res_scan_ftheta, frequency, "force", fig, force_ax, formatter)

    #param_ax = plt.Subplot(fig, gs00[1,2])
    # param display
    #ax = fig.add_subplot(param_ax)
    #ax.text(0.1, 0.7,
    #        "scan # = %d\n"\
    #        "time = %s\n"\
    #        "scan size = %s\n"\
    #        "scan step = %s\n"\
    #        "voltage = %s\n"\
    #        "pos_a = %s\n"\
    #        "x0 = %s\n"\
    #        "y0 = %s\n"\
    #        %(scan_n, time_stamp, scan_size, scan_step, voltage,
    #          init_pos_a, x0, y0),
    #        va="top", ha="left", fontsize=10.0)
    #ax.set_axis_off()
    
    gs0.tight_layout(fig, pad=0.25)
    save_fig(fig, "resonance_scan_" + str(scan_n), target)
    return 0

if __name__ == "__main__":
    init_target = get_host_data_folder()
    mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    day = raw_input("Enter day (dd): ")
    scan_n = raw_input("Enter scan: ")
    target = os.path.join(init_target, str(mon_yr))
    target = os.path.join(target, "day_" + str(day))
    target = os.path.join(target, "resonance_scans")
    target = os.path.join(target, "scan_" + str(scan_n))
    display_resonance_scan(target)
    plt.show()

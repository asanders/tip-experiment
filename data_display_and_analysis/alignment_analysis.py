import os
from igor.binarywave import load as loadibw
import sys
file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
version_dir = os.path.dirname(file_dir)
root_dir = os.path.dirname(version_dir)
# load computer definitions and data handling #
module_dir = os.path.join(root_dir, "igor-pro-tools")
if module_dir not in sys.path:
	sys.path.append(module_dir)
from definitions import *
from alignment_data_classes import *
import numpy as np

import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc
from matplotlib import dates
import matplotlib.gridspec as gridspec


def get_scan_list(scan_seq_dir, scan_seq):
    '''
    Returns a list of valid scans matching the scan sequence criteria.
    '''
    # isolate scan sequence in set of sequences #
    scans = [os.path.join(scan_seq_dir, scan)
             for scan in os.listdir(scan_seq_dir)
             if os.path.isdir(os.path.join(scan_seq_dir, scan))]
    scans_in_seq = []
    # look through scans for those matching the requested alignment set #
    for scan in scans:
        params = load_parameters(scan) # load scan parameters
        # fix any KeyError issues for missing/obselete entries #
        try: seq = int(params['alignment_set'])
        except KeyError: seq = 0
        # append data from all matching scans to storage arrays #
        if seq == scan_seq:
            # extract fitted centroids where possible #
            try:
                x0 = params['x0']
                y0 = params['y0']
            except KeyError:
                #print "KeyError (",os.path.basename(scan),")- x0,y0 not recorded: x0,y0 = 0"
                x0 = 'nan'
                y0 = 'nan'
            # only append if there was a fitted centroid #
            #print 'appending', os.path.basename(scan)
            #scans_in_seq.append(os.path.basename(scan))
            scans_in_seq.append(scan)
    return scans_in_seq

def get_scans(scan_seq_dir, seq):
    scan_list = get_scan_list(scan_seq_dir, seq)
    afm_scans = []
    for scan in scan_list:
        afm_scans.append(afm_alignment_data(scan))
    return afm_scans

def analyse_alignment_data(scan_seq_dir, seq = 0):
    afm_scans = get_scans(scan_seq_dir, seq)
    # create arrays of scan results #
    voltage = np.array([])
    position = np.array([])
    time = np.array([])
    scan_n = np.array([])
    amplitude = np.array([]).reshape((0,5))
    phase = np.array([]).reshape((0,5))
    for scan in afm_scans:
        voltage = np.append(voltage, scan.voltage)
        position = np.append(position, scan.position)
        time = np.append(time, scan.time)
        scan_n = np.append(scan_n, scan.scan_n)
        amplitude = np.vstack((amplitude, scan.amplitude_params))
        phase = np.vstack((phase, scan.phase_params))
    # make voltage segregated data #
    voltage = np.array([]).reshape((0,8))
    position = np.array([])
    time = np.array([])
    scan_n = np.array([]).reshape((0,8))
    amplitude = np.array([]).reshape((0,8,5))
    phase = np.array([]).reshape((0,8,5))
    ia = np.array([])
    step = np.array([])
    cycle = -1
    i_prev = 0
    for scan in afm_scans:
        #scan.fit_data()
        i = scan.voltage
        if i not in ia: ia = np.append(ia, i)
        if i > i_prev:
            cycle += 1
            step = np.append(step, cycle)
            voltage = np.vstack(( voltage, np.zeros((1,8)) ))
            scan_n = np.vstack(( scan_n, np.zeros((1,8)) ))
            amplitude = np.vstack(( amplitude, np.zeros((1,8,5)) ))
            phase = np.vstack(( phase, np.zeros((1,8,5)) ))
        voltage[cycle][i-3] = scan.voltage
        scan_n[cycle][i-3] = scan.scan_n
        amplitude[cycle][i-3] = scan.amplitude_params
        phase[cycle][i-3] = scan.phase_params
        i_prev = i
        
    voltage[voltage==0] = np.nan
    scan_n[scan_n==0] = np.nan
    amplitude[amplitude==0] = np.nan
    phase[phase==0] = np.nan
    
    step = step[:-2]
    amplitude = amplitude[:-2,:,:]
    phase = phase[:-2,:,:]
    
    # plot data #    
    fig = plt.figure()
    gs = gridspec.GridSpec(1,3)
    gs1 = gridspec.GridSpecFromSubplotSpec(2,1, subplot_spec=gs[0])
    plot_centroid_vs_step(gs1, ia, step, amplitude, phase)
    gs2 = gridspec.GridSpecFromSubplotSpec(2,1, subplot_spec=gs[1])
    plot_fwhm_vs_step(gs2, ia, step, amplitude, phase)
    gs3 = gridspec.GridSpecFromSubplotSpec(2,1, subplot_spec=gs[2])
    plot_peak_vs_step(gs3, ia, step, amplitude, phase)
    plt.tight_layout()
    gs.tight_layout(fig)
    # create save folder #
    day_folder = os.path.dirname(scan_seq_dir)
    analysis_folder = os.path.join(day_folder, 'analysis')
    if not os.path.exists(analysis_folder): os.makedirs(analysis_folder)
    fname = os.path.join(analysis_folder, "alignment_set_" + str(seq))
    print "saving figure to", fname, ".png"
    plt.savefig(fname + '.png', bbox_inches=0)
    plt.show()
    return 0

msize = 5
fs = 'full'
a = 0.75

#def plot_centroid_vs_scan_n(ax):
#    ax.plot(scan_n, amplitude[:,1], 'r-o', markersize=msize, fillstyle=fs, alpha=a)
#    ax.plot(scan_n, phase[:,1], 'r-s', markersize=msize, fillstyle=fs, alpha=a)
#    ax = ax.twinx()
#    ax.plot(scan_n, amplitude[:,2], 'b-o', markersize=msize, fillstyle=fs, alpha=a)
#    ax.plot(scan_n, phase[:,2], 'b-s', markersize=msize, fillstyle=fs, alpha=a)
#        
#def plot_fwhm_vs_scan_n(ax):
#    ax.plot(scan_n, amplitude[:,3], 'r-o', markersize=msize, fillstyle=fs, alpha=a)
#    ax.plot(scan_n, phase[:,3], 'r-s', markersize=msize, fillstyle=fs, alpha=a)
#    ax = ax.twinx()
#    ax.plot(scan_n, amplitude[:,4], 'b-o', markersize=msize, fillstyle=fs, alpha=a)
#    ax.plot(scan_n, phase[:,4], 'b-s', markersize=msize, fillstyle=fs, alpha=a)
#
#def plot_peak_vs_scan_n(ax):
#    ax.plot(scan_n, amplitude[:,0], 'r-o', markersize=msize, fillstyle=fs, alpha=a)
#    ax = ax.twinx()
#    ax.plot(scan_n, phase[:,0], 'r-s', markersize=msize, fillstyle=fs, alpha=a)

def plot_centroid_vs_step(gs, ia, step, amplitude, phase):
    x0_ax = plt.subplot(gs[0,0])
    y0_ax = plt.subplot(gs[1,0])
    x0_ax2 = x0_ax.twinx()
    y0_ax2 = y0_ax.twinx()
    ls = '-'#'none'
    for i in range(len(ia)):
        x0_ax.plot(step, amplitude[:,i,1], marker='o', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
        x0_ax2.plot(step, phase[:,i,1], marker='s', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
        y0_ax.plot(step, amplitude[:,i,2], marker='o', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
        y0_ax2.plot(step, phase[:,i,2], marker='s', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
    x0_ax.set_xlabel('step')
    y0_ax.set_xlabel('step')
    x0_ax.set_ylabel('x0 amplitude')
    y0_ax.set_ylabel('y0 amplitude')
    x0_ax2.set_ylabel('x0 phase')
    y0_ax2.set_ylabel('y0 phase')

def plot_fwhm_vs_step(gs, ia, step, amplitude, phase):
    xw_ax = plt.subplot(gs[0,0])
    yw_ax = plt.subplot(gs[1,0])
    xw_ax2 = xw_ax.twinx()
    yw_ax2 = yw_ax.twinx()
    ls = '-'#'none'
    #ax2 = ax.twinx()
    for i in range(len(ia)):
        xw_ax.plot(step, amplitude[:,i,3], marker='o', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
        xw_ax2.plot(step, phase[:,i,3], marker='s', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
        yw_ax.plot(step, amplitude[:,i,4], marker='o', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
        yw_ax2.plot(step, phase[:,i,4], marker='s', linestyle=ls, markersize=msize, fillstyle=fs, alpha=a)
    xw_ax.set_xlabel('step')
    yw_ax.set_xlabel('step')
    xw_ax.set_ylabel('x_fwhm amplitude')
    yw_ax.set_ylabel('y_fwhm amplitude')
    xw_ax2.set_ylabel('x_fwhm phase')
    yw_ax2.set_ylabel('y_fwhm phase')

def plot_peak_vs_step(gs, ia, step, amplitude, phase):
    a_ax = plt.subplot(gs[0,0])
    p_ax = plt.subplot(gs[1,0])
    ls = '-'#'none'
    #p_ax = a_ax.twinx()
    for i in range(len(ia)):
        a_ax.plot(step, amplitude[:,i,0], marker='o', linestyle=ls)
        p_ax.plot(step, phase[:,i,0], marker='s', linestyle=ls)
    a_ax.set_xlabel('step')
    p_ax.set_xlabel('step')
    a_ax.set_ylabel('peak amplitude')
    p_ax.set_ylabel('peak phase')

if __name__ == '__main__':
    init_target = get_host_data_folder()
    mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    day = raw_input("Enter day (dd): ")
    target = os.path.join(init_target, str(mon_yr))
    target = os.path.join(target, "day_" + str(day))
    scan_seq_dir = os.path.join(target, "alignment_scans")
    sequence = int(raw_input("Enter scan sequence: "))
    analyse_alignment_data(scan_seq_dir, sequence)
    #analyse_alignment_data("C:\\users\\alan\\desktop\\aug_2013\\day_02\\alignment_scans", 3)
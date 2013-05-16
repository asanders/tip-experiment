'''
Analyses tip alignment data.
'''

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

# load 3rd party modules #
from igor.binarywave import load as loadibw
import numpy as np
from scipy import ndimage
import datetime as dt
# load matplotlib modules #
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import proj3d
from matplotlib import dates

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
        params = load_params(scan)    # load scan parameters #
        # fix any KeyError issues for missing/obselete entries #
        try: seq = params['alignment_set']
        except KeyError:
            #print "KeyError (",os.path.basename(scan),") - alignment_set not recorded: seq = 0"
            seq = 0
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

def get_alignment_parameters(scans):
    scan_ns = np.array([])
    position_array = np.array([])
    voltage_array = np.array([])
    time_stamp_array = np.array([])
    for scan in scans:
        params = load_params(scan)
        scan_n = int(scan.rsplit('_',1)[1])
        position = params['init_pos_a']
        voltage = params['voltage']
        time_stamp = params['time_stamp'].strip('"')
        time_stamp = dt.datetime.strptime(time_stamp, '%H:%M:%S %d %b %Y')
        scan_ns = np.append(scan_ns, scan_n)
        position_array = np.append(position_array, position)
        voltage_array = np.append(voltage_array, voltage)
        time_stamp_array = np.append(time_stamp_array, time_stamp)
    position_array = 1000 * (position_array - position_array.min())
    # create a dictionary object of parameter arrays #
    parameter_arrays = {}
    parameter_arrays['scan_n'] = scan_ns
    parameter_arrays['voltage'] = voltage_array
    parameter_arrays['position'] = position_array
    parameter_arrays['time_stamp'] = time_stamp_array
    return parameter_arrays

def get_seq_variables(scans):
    #identify what variables were scanned during alignment #
    variables = []
    for scan in scans:
        waves = [wave for wave in os.listdir(scan)
                 if 'alignment_scan_' in wave
                 and '.ibw' in wave
                 and 'fit' not in wave]
        for wave in waves:
            var = (wave.split('.', 1)[0]).rsplit('_', 1)[1]
            if var == 'psd':
                var = 'y_psd'
            if var not in variables:
                variables.append(var)
    return variables

def get_seq_var_params(scans, var):
    '''
    Returns 5 arrays containing the gaussian fit parameters for the
    requested variable, var, for alignment scans in the list.
    '''
    # set up data storage arrays #
    x0_array = np.array([])
    y0_array = np.array([])
    amp_array = np.array([])
    x_fwhm_array = np.array([])
    y_fwhm_array = np.array([])
    # get the fit parameters for all valid alignment scans within all scans #
    for scan in scans:
        wave = 'alignment_scan_'+var+'.ibw'
        wave_loc = os.path.join(scan, wave)
        params = get_alignment_results(wave_loc) # must be given a file reference #
        amp_array = np.append(amp_array, params[0])
        x0_array = np.append(x0_array, params[1])
        x_fwhm_array = np.append(x_fwhm_array, params[2])
        y0_array = np.append(y0_array, params[3])
        y_fwhm_array = np.append(y_fwhm_array, params[4])
    return amp_array, x0_array, x_fwhm_array, y0_array, y_fwhm_array

def get_alignment_results(scan_array):
    '''
    Returns the fit parameters for the given alignment data array reference.
    The alignment data array reference is the (string) path to the filename.
    '''
    # load fit coefficient wave #
    fname = scan_array.rsplit('.', 1)[0]
    var = fname.rsplit('_', 1)[1]
    path = os.path.dirname(scan_array)
    w_coef = loadibw(os.path.join(path, var+"_w_coef.ibw"))
    w_coef = w_coef['wave']['wData']
    #w_sigma = loadibw(os.path.join(path, var+"_w_sigma.ibw"))
    #w_sigma = w_sigma['wave']['wData']
    
    # extract useful parameters - only valid for gaussian fit #
    # from igor - w_coef[0] = {z0, a0, x0, sigx, y0, sigy, corr}#
    bkgd = w_coef[0]
    amplitude = w_coef[1]
    x0 = w_coef[2]
    sig_x = w_coef[3]
    y0 = w_coef[4]
    sig_y = w_coef[5]
    corr = w_coef[6]
    # calculate useful parameters #
    x_fwhm = 2*np.sqrt(2*np.log(2))*sig_x
    y_fwhm = 2*np.sqrt(2*np.log(2))*sig_y
    results = np.array([amplitude, x0, x_fwhm, y0, y_fwhm])
    return results

def analyse_alignment_data(scan_seq_dir, scan_seq=0):
    '''
    Analyses a sequence of alignment scans.
    scan_seq_dir is a string, scan_seq is an integer #
    '''
    print "analysing alignment set", scan_seq, "in", scan_seq_dir
    scans = get_scan_list(scan_seq_dir, scan_seq)
    variables = get_seq_variables(scans)
    parameter_arrays = get_alignment_parameters(scans)
    # create save folder #
    day_folder = os.path.dirname(scan_seq_dir)
    analysis_folder = check_folder(os.path.join(day_folder, 'analysis'))
    set_folder = check_folder(os.path.join(analysis_folder,\
                                           'alignment_set_'+str(scan_seq)))
    # save arrays #
    np.save(os.path.join(set_folder, 'positions.npy'), parameter_arrays['position'])
    np.save(os.path.join(set_folder, 'voltages.npy'), parameter_arrays['voltage'])
    np.save(os.path.join(set_folder, 'time_stamps.npy'), parameter_arrays['time_stamp'])
    
    for var in variables:
        globals()[var+'_amp'], globals()[var+'_x0'], globals()[var+'_x_fwhm'],\
        globals()[var+'_y0'], globals()[var+'_y_fwhm']\
        = get_seq_var_params(scans, var)
        # save arrays #
        np.save(os.path.join(set_folder, var+'_amp' + '.npy'), globals()[var+'_amp'])
        np.save(os.path.join(set_folder, var+'_x0' + '.npy'), globals()[var+'_x0'])
        np.save(os.path.join(set_folder, var+'_x_fwhm' + '.npy'), globals()[var+'_x_fwhm'])
        np.save(os.path.join(set_folder, var+'_y0' + '.npy'), globals()[var+'_y0'])
        np.save(os.path.join(set_folder, var+'_y_fwhm' + '.npy'), globals()[var+'_y_fwhm'])
    
    # display analysed alignment data #
    # setup figure #
    fig_width_cm = 40.0
    inches_per_cm = 1.0/2.54
    fig_width = fig_width_cm * inches_per_cm
    fig_height = (2.0/5.0) * fig_width
    fig_size = (fig_width, fig_height)
    fig_params = {'backend': 'ps',
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
    plt.rcParams.update(fig_params)
    plt.rcParams['legend.loc'] = 'best'

    # define function to add subplot #
    def add_analysis_subplot(ax, source, x, y_param, x_label='', y_label=''):
        '''
        Adds a subplot to an alignment analysis figure
        ax is a subplot axis.
        source is either 'I' for current or 'F' for force.
        param is either 'x0', 'y0', 'x_fwhm', 'y_fwhm' or 'amp'.
        x and y are data arrays with labels x_label and y_label.
        '''
        if source == 'I': vs = ['r', 'theta']
        elif source == 'F': vs = ['fr', 'ftheta']
        # set marker colours to red and blue #
        ax.set_color_cycle(['r', 'b'])
        ax2_exists = False
        for var in (v for v in variables if v in vs):
            if var == 'r': name = r'$I_r$'
            elif var == 'theta': name = r'$I_\theta$'
            elif var == 'fr': name = r'$F_r$'
            elif var == 'ftheta': name = r'$F_\theta$'
            # override axis if twinned axes with different scales are used #
            if y_param == 'amp' and (var == 'fr' or var == 'r'):
                ax2 = ax; ax2_exists = True
                label = y_label.split('{', 1)[0]+'{r,'+y_label.split('{', 1)[1]
                ax.set_ylabel(label)
            elif y_param == 'amp' and (var == 'ftheta' or var == 'theta'):
                ax = ax.twinx()
                label = y_label.split('{', 1)[0]+'{\\theta,'+y_label.split('{', 1)[1]
                ax.set_ylabel(label)
            line = ax.errorbar(x, globals()[var+'_'+y_param],
                              #yerr=vars()[var+'_'+param+'_error'],
                              fmt='o', linestyle='', markersize=4, label=name)
        #ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
        #        fontsize=10, fontweight='bold', transform=ax.transAxes)
        lines, labels = ax.get_legend_handles_labels()
        if ax2_exists:
            axlines, axlabels = ax2.get_legend_handles_labels()
            lines += axlines
            labels += axlabels
        ax.legend(lines, labels, loc='best')
        if 'voltage' in x_label or 'scan' in x_label:
            ax.set_xlim(0.9*x.min(), 1.1*x.max())
        elif 'time' in x_label:
            time_format = dates.DateFormatter('%H:%M')
            ax.xaxis.set_major_formatter(time_format)
            labels = ax.get_xticklabels()
            for label in labels:
                label.set_fontsize(10)
                label.set_rotation(60)
            if ax2_exists:
                ax2.xaxis.set_major_formatter(time_format)
                labels = ax2.get_xticklabels()
                for label in labels:
                    label.set_fontsize(10)
                    label.set_rotation(60)
        #ax.set_ylim(0.9*y.min(), 1.1*y.max())
        ax.set_xlabel(x_label)
        if y_param != 'amp':
            ax.set_ylabel(y_label)        
        return 0

    def add_analysis_figure(parameter, plabel):
        # plot figure #
        fig = plt.figure()
        # force subplots #
        ax = fig.add_subplot(251)
        add_analysis_subplot(ax, 'F', parameter_arrays[parameter], 'x0',\
                             x_label=plabel, y_label='$x_0$')
        ax = fig.add_subplot(252)
        add_analysis_subplot(ax, 'F', parameter_arrays[parameter], 'y0',\
                             x_label=plabel, y_label='$y_0$')
        ax = fig.add_subplot(253)
        add_analysis_subplot(ax, 'F', parameter_arrays[parameter], 'x_fwhm',\
                             x_label=plabel, y_label='$x_{fwhm}$')
        ax = fig.add_subplot(254)
        add_analysis_subplot(ax, 'F', parameter_arrays[parameter], 'y_fwhm',\
                             x_label=plabel, y_label='$y_{fwhm}$')
        ax = fig.add_subplot(255)
        add_analysis_subplot(ax, 'F', parameter_arrays[parameter], 'amp',\
                             x_label=plabel, y_label='$F_{amp}$')
        # current subplots #
        ax = fig.add_subplot(256)
        add_analysis_subplot(ax, 'I', parameter_arrays[parameter], 'x0',\
                             x_label=plabel, y_label='$x_0$')
        ax = fig.add_subplot(257)
        add_analysis_subplot(ax, 'I', parameter_arrays[parameter], 'y0',\
                             x_label=plabel, y_label='$y_0$')
        ax = fig.add_subplot(258)
        add_analysis_subplot(ax, 'I', parameter_arrays[parameter], 'x_fwhm',\
                             x_label=plabel, y_label='$x_{fwhm}$')
        ax = fig.add_subplot(259)
        add_analysis_subplot(ax, 'I', parameter_arrays[parameter], 'y_fwhm',\
                             x_label=plabel, y_label='$y_{fwhm}$')
        ax = fig.add_subplot(2,5,10)
        add_analysis_subplot(ax, 'I', parameter_arrays[parameter], 'amp',\
                             x_label=plabel, y_label='$I_{amp}$')
        plt.tight_layout()
        fname = os.path.join(analysis_folder, "alignment_set_" + str(scan_seq) + ' - fit vs ' + parameter)
        print "saving figure to", fname, ".png"
        plt.savefig(fname + '.png', bbox_inches=0)
        return 0

    add_analysis_figure('voltage', 'voltage (V)')
    add_analysis_figure('scan_n', 'scan #')
    add_analysis_figure('time_stamp', 'time')
    add_analysis_figure('position', 'position (nm)')

    voltages = parameter_arrays['voltage']
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot(121)
    ax.plot(voltages, 1000*(globals()['fr_x0']-globals()['ftheta_x0']),
            'k', marker='o', markersize=4, linestyle='')
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('$\Delta x_0$ (nm)')
    ax.set_xlim(0.9*voltages.min(), 1.1*voltages.max())
    
    ax = fig.add_subplot(122)
    ax.plot(voltages, 1000*(globals()['fr_y0']-globals()['ftheta_y0']),
            'k', marker='o', markersize=4, linestyle='')
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('$\Delta y_0$ (nm)')
    ax.set_xlim(0.9*voltages.min(), 1.1*voltages.max())
    
    plt.tight_layout()
    fname = os.path.join(analysis_folder, "alignment_set_" + str(scan_seq) + " - amplitude-phase deviation")
    print "saving figure to", fname, ".png"
    plt.savefig(fname + '.png', bbox_inches=0)
    return 0

if __name__ == '__main__':
    init_target = get_host_data_folder()
    mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    day = raw_input("Enter day (dd): ")
    target = os.path.join(init_target, str(mon_yr))
    target = os.path.join(target, "day_" + str(day))
    scan_seq_dir = os.path.join(target, "alignment_scans")
    sequence = input("Enter scan sequence: ")
    analyse_alignment_data(scan_seq_dir, sequence)
    plt.show()
    

"""
Analyses tip alignment data.
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

# load 3rd party modules #
from igor.binarywave import load as loadibw
import numpy as np
from scipy import ndimage
# load matplotlib modules #
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import proj3d

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
        try:    # alignment set #
            seq = params['alignment_set']
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
    position_array = np.array([])
    voltage_array = np.array([])
    for scan in scans:
        params = load_params(scan)
        position = params['init_pos_a']
        voltage = params['voltage']
        position_array = np.append(position_array, position)
        voltage_array = np.append(voltage_array, voltage)
    position_array = 1000 * (position_array - position_array.min())
    return position_array, voltage_array

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

def analyse_alignment_data(scan_seq_dir, scan_seq):
    '''
    Analyses a sequence of alignment scans.
    scan_seq_dir is a string, scan_seq is an integer #
    '''
    print "analysing alignment set", scan_seq, "in", scan_seq_dir
    scans = get_scan_list(scan_seq_dir, scan_seq)
    variables = get_seq_variables(scans)
    positions, voltages = get_alignment_parameters(scans)
    # create save folder #
    day_folder = os.path.dirname(scan_seq_dir)
    analysis_folder = check_folder(os.path.join(day_folder, 'analysis'))
    set_folder = check_folder(os.path.join(analysis_folder,\
                                           'alignment_set_'+scan_seq))
    # save arrays #
    np.save(os.path.join(set_folder, 'positions.npy'), positions)
    np.save(os.path.join(set_folder, 'voltages.npy'), voltages)
    for var in variables:
        vars()[var+'_amp'], vars()[var+'_x0'], vars()[var+'_x_fwhm'],\
        vars()[var+'_y0'], vars()[var+'_y_fwhm']\
        = get_seq_var_params(scans, var)
        # save arrays #
        np.save(os.path.join(set_folder, var+'_amp' + '.npy'), vars()[var+'_amp'])
        np.save(os.path.join(set_folder, var+'_x0' + '.npy'), vars()[var+'_x0'])
        np.save(os.path.join(set_folder, var+'_x_fwhm' + '.npy'), vars()[var+'_x_fwhm'])
        np.save(os.path.join(set_folder, var+'_y0' + '.npy'), vars()[var+'_y0'])
        np.save(os.path.join(set_folder, var+'_y_fwhm' + '.npy'), vars()[var+'_y_fwhm'])
    
    # display analysed alignment data #
    fig = plt.figure()
    ax = fig.add_subplot(251)
    for var in (v for v in variables if v == 'fr' or v == 'ftheta'):
        sax = ax.errorbar(voltages, vars()[var+'_x0'],
                          #yerr=vars()[var+'_x_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('x0')

    ax = fig.add_subplot(252)
    for var in (v for v in variables if v == 'fr' or v == 'ftheta'):
        sax = ax.errorbar(voltages, vars()[var+'_y0'],
                          #yerr=vars()[var+'_y_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('y0')

    ax = fig.add_subplot(253)
    for var in (v for v in variables if v == 'fr' or v == 'ftheta'):
        sax = ax.errorbar(voltages, vars()[var+'_x_fwhm'],
                          #yerr=vars()[var+'_x_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('x_fwhm')

    ax = fig.add_subplot(254)
    for var in (v for v in variables if v == 'fr' or v == 'ftheta'):
        sax = ax.errorbar(voltages, vars()[var+'_y_fwhm'],
                          #yerr=vars()[var+'_y_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('y_fwhm')

    ax = fig.add_subplot(255)
    for var in (v for v in variables if v == 'fr' or v == 'ftheta'):
        sax = ax.errorbar(voltages, vars()[var+'_amp'],
                          #yerr=vars()[var+'_y_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('amp')

    ax = fig.add_subplot(256)
    for var in (v for v in variables if v == 'r' or v == 'theta'):
        sax = ax.errorbar(voltages, vars()[var+'_x0'],
                          #yerr=vars()[var+'_x_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('x0')

    ax = fig.add_subplot(257)
    for var in (v for v in variables if v == 'r' or v == 'theta'):
        sax = ax.errorbar(voltages, vars()[var+'_y0'],
                          #yerr=vars()[var+'_y_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('y0')

    ax = fig.add_subplot(258)
    for var in (v for v in variables if v == 'r' or v == 'theta'):
        sax = ax.errorbar(voltages, vars()[var+'_x_fwhm'],
                          #yerr=vars()[var+'_x_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('x_fwhm')

    ax = fig.add_subplot(259)
    for var in (v for v in variables if v == 'r' or v == 'theta'):
        sax = ax.errorbar(voltages, vars()[var+'_y_fwhm'],
                          #yerr=vars()[var+'_y_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('y_fwhm')

    ax = fig.add_subplot(2510)
    for var in (v for v in variables if v == 'r' or v == 'theta'):
        sax = ax.errorbar(voltages, vars()[var+'_amp'],
                          #yerr=vars()[var+'_y_fwhm'],
                          fmt='o')
        ax.text(0.05, 0.95, var, ha='left', va='top', color='black',
                fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.set_xlabel('voltage (V)')
    ax.set_ylabel('amp')
    
    plt.tight_layout()
    day_folder = os.path.dirname(scan_seq_dir)
    fname = os.path.join(day_folder, "alignment_set_" + str(scan_seq))
    print "saving figure to", fname, ".png"
    plt.savefig(fname + '.png', bbox_inches=0)
    
    return 0

def display_scan_seq(scan_seq_dir, scan_seq):
    # scan_seq_dir is a string, scan_seq is an integer #
    print "analysing alignment set", scan_seq, "in", scan_seq_dir

    ## IDENTIFYING DATA ##
    # isolate scan sequence in set of sequences #
    scans = [os.path.join(scan_seq_dir, scan)
             for scan in os.listdir(scan_seq_dir)
             if os.path.isdir(os.path.join(scan_seq_dir, scan))]
    scans_in_seq = []
    
    # data storage arrays #
    # scan parameters #
    voltages = np.array([])
    positions = np.array([])
    # fitted centroid #
    x0s = np.array([])
    y0s = np.array([])
    # electronic centroids #
    x_x0s = np.array([])
    x_y0s = np.array([])
    y_x0s = np.array([])
    y_y0s = np.array([])
    r_x0s = np.array([])
    r_y0s = np.array([])
    theta_x0s = np.array([])
    theta_y0s = np.array([])
    psd_x0s = np.array([])
    psd_y0s = np.array([])
    # force centroids #
    fx_x0s = np.array([])
    fx_y0s = np.array([])
    fy_x0s = np.array([])
    fy_y0s = np.array([])
    fr_x0s = np.array([])
    fr_y0s = np.array([])
    ftheta_x0s = np.array([])
    ftheta_y0s = np.array([])

    # look through scans for those matching the requested alignment set #
    for scan in scans:
        # load scan parameters to identify valid scans #
        params = load_params(target)

        # fix any KeyError issues for missing/obselete entries #
        try:    # alignment set #
            seq = params['alignment_set']
        except KeyError:
            print "KeyError (",os.path.basename(scan),") - alignment_set not recorded: seq = 0"
            seq = 0
        #print 'seq =', seq

        # identify whether scan used electronic and/or force alignment techniques #
        try:
            electronic_alignment = params['electronic_alignment']
        except KeyError:
            electronic_alignment = 1
        try:
            force_alignment = params['force_alignment']
        except KeyError:
            force_alignment = 0

        ## EXTRACTING DATA ##
        # append data from all matching scans to storage arrays #
        if seq == scan_seq:
            # extract fitted centroids where possible #
            try:
                x0 = params['x0']
                y0 = params['y0']
            except KeyError:
                print "KeyError (",os.path.basename(scan),")- x0,y0 not recorded: x0,y0 = 0"
                x0 = 0
                y0 = 0
                #continue
            
            # only append if there was a fitted centroid #
            print 'appending', os.path.basename(scan)
            scans_in_seq.append(os.path.basename(scan))
            # extract relevant parameters #
            voltages = np.append(voltages, params['voltage'])
            positions = np.append(positions, params['init_pos_a'])
            x0s = np.append(x0s, x0)
            y0s = np.append(y0s, y0)
            
            # extract electronic centroids where possible #
            if electronic_alignment:
                # x #
                try:
                    x0 = params['x_x0']
                    y0 = params['x_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                x_x0s = np.append(x_x0s, x0)
                x_y0s = np.append(x_y0s, y0)
                # y #
                try:
                    x0 = params['y_x0']
                    y0 = params['y_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                y_x0s = np.append(y_x0s, x0)
                y_y0s = np.append(y_y0s, y0)
                # r #
                try:
                    x0 = params['r_x0']
                    y0 = params['r_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                r_x0s = np.append(r_x0s, x0)
                r_y0s = np.append(r_y0s, y0)
                # theta #
                try:
                    x0 = params['theta_x0']
                    y0 = params['theta_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                theta_x0s = np.append(theta_x0s, x0)
                theta_y0s = np.append(theta_y0s, y0)
                # psd #
                try:
                    x0 = params['psd_x0']
                    y0 = params['psd_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                psd_x0s = np.append(psd_x0s, x0)
                psd_y0s = np.append(psd_y0s, y0)
            # extract force centroids where possible #
            if force_alignment:
                # fx #
                try:
                    x0 = params['fx_x0']
                    y0 = params['fx_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                fx_x0s = np.append(fx_x0s, x0)
                fx_y0s = np.append(fx_y0s, y0)
                # fy #
                try:
                    x0 = params['fy_x0']
                    y0 = params['fy_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                fy_x0s = np.append(fy_x0s, x0)
                fy_y0s = np.append(fy_y0s, y0)
                # fr #
                try:
                    x0 = params['fr_x0']
                    y0 = params['fr_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                fr_x0s = np.append(fr_x0s, x0)
                fr_y0s = np.append(fr_y0s, y0)
                # ftheta #
                try:
                    x0 = params['ftheta_x0']
                    y0 = params['ftheta_y0']
                except KeyError:
                    x0 = 0
                    y0 = 0
                ftheta_x0s = np.append(ftheta_x0s, x0)
                ftheta_y0s = np.append(ftheta_y0s, y0)
            
    #print "scans in seq =", scans_in_seq

    # adjust data #
    positions = positions - positions.min()

    ## DATA LOADED ##
    ## PLOT DATA ##
    # set up figure properties for all figures #
    fig_width_cm = 25.0
    inches_per_cm = 1.0/2.54
    fig_width = fig_width_cm * inches_per_cm
    golden_mean = (np.sqrt(5)-1.0)/2.0         # Aesthetic ratio
    fig_height = golden_mean * fig_width
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
            'figure.subplot.wspace' : 0.04,
            'figure.subplot.hspace' : 0.00,
            'figure.figsize': fig_size}
    plt.rcParams.update(params)
    #plt.close('all')

    ## SCATTER PLOT OF FITTED CENTROIDS VS VOLTAGE AND POSITION ##
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='3d')
    ax.view_init(elev=20.0, azim=-45.0)
    ax.scatter(voltages, positions, x0s)
    ax.set_xlabel('voltage')
    ax.set_ylabel('axial position')
    ax.set_zlabel('x0')

    ax = fig.add_subplot(122, projection='3d')
    ax.view_init(elev=20.0, azim=-45.0)
    ax.scatter(voltages, positions, y0s)
    ax.set_xlabel('voltage')
    ax.set_ylabel('axial position')
    ax.set_zlabel('y0')

    plt.tight_layout()
    #alignment_folder = os.path.dirname(scan_seq_dir)
    day_folder = os.path.dirname(scan_seq_dir)
    fname = os.path.join(day_folder, "alignment_set_" + str(scan_seq)) + "_3d"
    print "saving figure to", fname, ".png"
    plt.savefig(fname + '.png', bbox_inches=0)

    ## FITTED CENTROIDS AS A FUNCTION OF POSITION AND VOLTAGE ##
    fig = plt.figure()
    ax = fig.add_subplot(121)
    sax = ax.scatter(positions, x0s, c=voltages, marker='o', s=40, cmap=cm.jet)
    ax.set_xlabel('axial position')
    ax.set_ylabel('x0')
    cb = plt.colorbar(sax, shrink=0.75)
    cb.set_label('voltage')

    ax = fig.add_subplot(122)
    sax = ax.scatter(positions, y0s, c=voltages, marker='o', s=40, cmap=cm.jet)
    ax.set_xlabel('axial position')
    ax.set_ylabel('y0')
    cb = plt.colorbar(sax, shrink=0.75)
    cb.set_label('voltage')

    plt.tight_layout()
    day_folder = os.path.dirname(scan_seq_dir)
    fname = os.path.join(day_folder, "alignment_set_" + str(scan_seq))
    print "saving figure to", fname, ".png"
    plt.savefig(fname + '.png', bbox_inches=0)

    ## PLOT ALL CENTROID FITS FOR EACH SCAN IN THE SET ##
    fig = plt.figure()
    ax = fig.add_subplot(121)
    if electronic_alignment:
        sax = ax.scatter(positions, x_x0s, c=voltages, marker='v', s=40,
                         alpha=0.6, cmap=cm.jet, label='$x$')
        sax = ax.scatter(positions, y_x0s, c=voltages, marker='^', s=40,
                         alpha=0.6, cmap=cm.jet, label='$y$')
        sax = ax.scatter(positions, r_x0s, c=voltages, marker='<', s=40,
                         alpha=0.6, cmap=cm.jet, label='$r$')
        sax = ax.scatter(positions, theta_x0s, c=voltages, marker='>', s=40,
                         alpha=0.6, cmap=cm.jet, label='$\theta$')
        sax = ax.scatter(positions, psd_x0s, c=voltages, marker='h', s=40,
                         alpha=0.6, cmap=cm.jet, label='$V_psd$')
    if force_alignment:
        sax = ax.scatter(positions, fx_x0s, c=voltages, marker='o', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_x$')
        sax = ax.scatter(positions, fy_x0s, c=voltages, marker='s', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_y$')
        sax = ax.scatter(positions, fr_x0s, c=voltages, marker='*', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_r$')
        sax = ax.scatter(positions, ftheta_x0s, c=voltages, marker='p', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_\theta$')
    ax.set_xlabel('axial position')
    ax.set_ylabel('x0')
    ax.legend()
    cb = plt.colorbar(sax, shrink=0.75)
    cb.set_label('voltage')

    ax = fig.add_subplot(122)
    if electronic_alignment:
        sax = ax.scatter(positions, x_y0s, c=voltages, marker='v', s=40,
                         alpha=0.6, cmap=cm.jet, label='$x$')
        sax = ax.scatter(positions, y_y0s, c=voltages, marker='^', s=40,
                         alpha=0.6, cmap=cm.jet, label='$y$')
        sax = ax.scatter(positions, r_y0s, c=voltages, marker='<', s=40,
                         alpha=0.6, cmap=cm.jet, label='$r$')
        sax = ax.scatter(positions, theta_y0s, c=voltages, marker='>', s=40,
                         alpha=0.6, cmap=cm.jet, label='$\theta$')
        sax = ax.scatter(positions, psd_y0s, c=voltages, marker='h', s=40,
                         alpha=0.6, cmap=cm.jet, label='$V_psd$')
    if force_alignment:
        sax = ax.scatter(positions, fx_y0s, c=voltages, marker='o', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_x$')
        sax = ax.scatter(positions, fy_y0s, c=voltages, marker='s', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_y$')
        sax = ax.scatter(positions, fr_y0s, c=voltages, marker='*', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_r$')
        sax = ax.scatter(positions, ftheta_y0s, c=voltages, marker='p', s=40,
                         alpha=0.6, cmap=cm.jet, label='$F_\theta$')
    ax.set_xlabel('axial position')
    ax.set_ylabel('y0')
    cb = plt.colorbar(sax, shrink=0.75)
    cb.set_label('voltage')

    plt.tight_layout()
    day_folder = os.path.dirname(scan_seq_dir)
    fname = os.path.join(day_folder, "scan_set_" + str(scan_seq))
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
    

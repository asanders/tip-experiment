"""
Plots tip experiment data in a more useful display.
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
from analysis_tools import *

# load 3ds party modules #
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
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

################################################################################

def add_qc_spec_subplot(fig, ax1, wave, name, xwave=None, ywave=None, xname='', yname=''):
    wave = ndimage.gaussian_filter(wave, 0.7)
    Z = wave
    if xwave == None:
        xwave = np.linspace(0, Z.shape[1], Z.shape[1])
    if ywave == None:
        ywave = np.linspace(0, Z.shape[0], Z.shape[0])
    X = xwave
    Y = ywave
    X, Y = np.linspace(X.min(), X.max(), len(X)), np.linspace(Y.min(), Y.max(), len(Y))
    X, Y = np.meshgrid(X, Y)

    x_offset = 0.5*(X.max()-X.min())
    y_offset = 0.5*(Y.max()-Y.min())
    z_offset = 0.75*(Z.max()-Z.min())

    c_levels = np.linspace(Z.min(), 1.05*Z.max(), 100)
    l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
    cmap = cm.Spectral_r
    norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
    lw = 0.5
    
    ax = fig.add_subplot(ax1)
    cfax = ax.contourf(X, Y, Z, c_levels,
                       norm=norm,
                       alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    #cax = ax.contour(X, Y, Z, l_levels,
    #                  norm=norm,
    #                  linewidths=lw,
    #                  colors='k', linestyles='solid')

    # figure formatting
    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter)
    
    # step axis
    for label in ax.get_yticklabels():
        label.set_visible(False)

    ax.minorticks_on()
    ax.set_xlabel(xname)
    #ax.set_xlim(500e-9, 900e-9)
    ax.set_ylabel(yname)
    
    # colour bars
    cb = plt.colorbar(cfax, shrink=1.0, extend='both')
    cb.set_label('optical scattering (a.u.)')
    return 0

def add_qc_cond_subplot(fig, ax, cond, current, time=None):
    if time == None:
        time = np.linspace(0, len(cond), len(cond))
    
    # conductance
    ax = fig.add_subplot(ax)
    ax.plot(cond, time, 'k-')
    loc = ax.xaxis.get_major_locator()
    loc.numticks = 5
    x_range = cond.max() - cond.min()
    ax.set_xlim(cond.min() - 0.05*x_range, cond.max()+ 0.05*x_range)
    ax.invert_xaxis()
    ax.set_xlabel("$G$ ($G_0$)")
    labels = ax.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)

    # step axis
    #ax.set_ylim(0, len(cond))
    for label in ax.get_yticklabels():
        label.set_visible(False)

    # current
    ax2 = ax.twiny()
    ax2.plot(current, time, 'k-')
    loc = ax2.xaxis.get_major_locator()
    loc.numticks = 5
    x_range = current.max() - current.min()
    ax2.set_xlim(current.min() - 0.05*x_range, current.max()+ 0.05*x_range)
    ax2.invert_xaxis()
    ax2.set_xlabel("$I (A)$")
    labels = ax2.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)

    ax.minorticks_on()
    return 0

def add_qc_force_subplot(fig, ax, psd, time=None):
    if time == None:
        time = np.linspace(0, len(psd), len(psd))
    
    # lateral force
    ax = fig.add_subplot(ax)
    ax.plot(psd, time, 'r-')
    loc = ax.xaxis.get_major_locator()
    loc.numticks = 2
    x_range = psd.max() - psd.min()
    ax.set_xlim(psd.min() - 0.05*x_range, psd.max() + 0.05*x_range)
    ax.invert_xaxis()
    ax.set_xlabel("$V_{y,psd}$ (V)")
    labels = ax.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)
    ax.xaxis.set_major_locator(MaxNLocator(5))

    # step axis    
    ax.set_ylim(0, len(psd))
    ax.set_ylabel("time (ms)")

    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter) 
    ax.yaxis.set_major_formatter(formatter)
    ax.minorticks_on()
    return 0

def display_time_resolved_experiment_scan(target, instance):
    data_path = os.path.join(target, "time_resolved_data")
    # load temporal data in target folder with a given step reference
    instance = str(instance)
    # spectra
    spec2d = loadibw(os.path.join(data_path, "qc_spec_"+instance+".ibw"))
    spec2d = spec2d['wave']['wData']
    spec2d = spec2d.T
    # conductance and force
    current = loadibw(os.path.join(data_path, "qc_trace_"+instance+".ibw"))
    current = current['wave']['wData']
    cond = loadibw(os.path.join(data_path, "qcg_trace_"+instance+".ibw"))
    cond = cond['wave']['wData']
    psd = loadibw(os.path.join(data_path, "qc_force_"+instance+".ibw"))
    psd = psd['wave']['wData']
    # parameters

    # extract parameter data
    ###

    # isolate spectral region of interest
    # set up the figure
    fig_width_cm = 25.0
    inches_per_cm = 1.0/2.54
    fig_width = fig_width_cm * inches_per_cm
    fig_height = 0.75 * fig_width
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
    fig = plt.figure()
    # setup subplots
    gs0 = gridspec.GridSpec(1, 2)
    spec_ax = 122
    spec_ax = plt.Subplot(fig, gs0[0, 1])
    gs00 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs0[0])
    cond_ax = plt.Subplot(fig, gs00[0, 1], sharey=spec_ax)
    f_ax = plt.Subplot(fig, gs00[0, 0], sharey=spec_ax)
    # plot data
    add_qc_spec_subplot(fig, spec_ax, spec2d, 'spec',
                     xwave=None, ywave=None,
                     xname='', yname='')
    add_qc_cond_subplot(fig, cond_ax, cond, current)
    add_qc_force_subplot(fig, f_ax, psd)
    #plt.tight_layout()
    gs0.tight_layout(fig, pad=0.25)#, w_pad=0.1, h_pad=0.1)

    scan_n = os.path.basename(target).rsplit("_", 1)[1]
    save_fig(fig, "tip_scan_" + scan_n + "_temporal_data_" + instance, target)
    return 0

################################################################################

def add_spec_subplot(fig, ax1, wave, name, xwave=None, ywave=None, xname='', yname=''):
    wave = ndimage.gaussian_filter(wave, 0.7)
    Z = wave
    if xwave == None:
        xwave = np.linspace(0, Z.shape[1], Z.shape[1])
    if ywave == None:
        ywave = np.linspace(0, Z.shape[0], Z.shape[0])
    X = xwave
    Y = ywave
    X, Y = np.linspace(X.min(), X.max(), len(X)), np.linspace(Y.min(), Y.max(), len(Y))
    X, Y = np.meshgrid(X, Y)

    x_offset = 0.5*(X.max()-X.min())
    y_offset = 0.5*(Y.max()-Y.min())
    z_offset = 0.75*(Z.max()-Z.min())

    c_levels = np.linspace(Z.min(), 1.05*Z.max(), 100)
    l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
    cmap = cm.Spectral_r
    norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
    lw = 0.5
    
    ax = fig.add_subplot(ax1)
    cfax = ax.contourf(X, Y, Z, c_levels,
                       norm=norm,
                       alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    #cax = ax.contour(X, Y, Z, l_levels,
    #                  norm=norm,
    #                  linewidths=lw,
    #                  colors='k', linestyles='solid')

    # figure formatting
    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter)
    
    # step axis
    for label in ax.get_yticklabels():
        label.set_visible(False)

    ax.minorticks_on()
    ax.set_xlabel(xname)
    #ax.set_xlim(500e-9, 900e-9)
    ax.set_ylabel(yname)
    
    # colour bars
    cb = plt.colorbar(cfax, shrink=1.0, extend='both')
    cb.set_label('optical scattering (a.u.)')
    return 0

def add_cond_subplot(fig, ax, cond, current):
    # conductance
    ax = fig.add_subplot(ax)
    ax.plot(cond, np.linspace(0, len(cond), len(cond)), 'k-')
    ax.set_xscale('log')
    loc = ax.xaxis.get_major_locator()
    loc.numticks = 5
    x_range = cond.max() - cond.min()
    ax.set_xlim(cond.min() - 0.05*x_range, cond.max()+ 0.05*x_range)
    ax.invert_xaxis()
    ax.set_xlabel("$G$ ($G_0$)")
    labels = ax.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)

    # step axis
    #ax.set_ylim(0, len(cond))
    for label in ax.get_yticklabels():
        label.set_visible(False)

    # current
    ax2 = ax.twiny()
    ax2.plot(current, np.linspace(0, len(current), len(current)), 'k-')
    ax2.set_xscale('log')
    loc = ax2.xaxis.get_major_locator()
    loc.numticks = 5
    x_range = current.max() - current.min()
    ax2.set_xlim(current.min() - 0.05*x_range, current.max()+ 0.05*x_range)
    ax2.invert_xaxis()
    ax2.set_xlabel("$I (A)$")
    labels = ax2.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)

    ax.minorticks_on()
    return 0

def add_force_subplot(fig, ax, psd_x, psd_y):
    # lateral force
    ax = fig.add_subplot(ax)
    ax.plot(psd_y, np.linspace(0, len(psd_y), len(psd_y)), 'r-')
    loc = ax.xaxis.get_major_locator()
    loc.numticks = 2
    x_range = psd_y.max() - psd_y.min()
    ax.set_xlim(psd_y.min() - 0.05*x_range, psd_y.max() + 0.05*x_range)
    ax.invert_xaxis()
    ax.set_xlabel("$V_{y,psd}$ (V)")
    labels = ax.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)
    ax.xaxis.set_major_locator(MaxNLocator(5))

    # step axis
    #ax.set_ylim(0, len(psd_y))
    for label in ax.get_yticklabels():
        label.set_visible(False)

    # torsional force
    ax2 = ax.twiny()
    ax2.plot(psd_x, np.linspace(0, len(psd_x), len(psd_x)), 'b-')
    loc = ax2.xaxis.get_major_locator()
    loc.numticks = 2
    x_range = psd_x.max() - psd_x.min()
    ax2.set_xlim(psd_x.min() - 0.05*x_range, psd_x.max() + 0.05*x_range)
    ax2.invert_xaxis()
    ax2.set_xlabel("$V_{x,psd}$ (V)")
    labels = ax2.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)
    ax2.xaxis.set_major_locator(MaxNLocator(5))
    
    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_formatter(formatter)
    
    ax.minorticks_on()
    ax2.minorticks_on()
    return 0

def add_disp_subplot(fig, ax, disp):
    # displacement
    ax = fig.add_subplot(ax)
    ax.plot(disp, np.linspace(0, len(disp), len(disp)), 'k-')
    loc = ax.xaxis.get_major_locator()
    loc.numticks = 2
    x_range = disp.max() - disp.min()
    ax.set_xlim(disp.min() - 0.05*x_range, disp.max() + 0.05*x_range)
    ax.invert_xaxis()
    ax.set_xlabel("$z_{PZ}$ (nm)")
    labels = ax.get_xticklabels()
    for label in labels:
        label.set_fontsize(10)
        label.set_rotation(90)

    # step axis
    ax.set_ylim(0, len(disp))
    ax.set_ylabel("step")

    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter) 
    ax.yaxis.set_major_formatter(formatter)
    
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.minorticks_on()
    
    return 0

def display_experiment_scan(target):
    ## load spatial data in target folder ##
    # spectra #
    spec2d = loadibw(os.path.join(target, "spec2d.ibw"))
    spec2d = spec2d['wave']['wData']
    spec2d = spec2d.T
    wav = loadibw(os.path.join(target, "wavelength.ibw"))
    wav = wav['wave']['wData']
    try:
            dual_pol = True
            spec2d_t = loadibw(os.path.join(target, "spec2d_t.ibw"))
            spec2d_t = spec2d_t['wave']['wData']
            spec2d_t = spec2d_t.T
            wav_t = loadibw(os.path.join(target, "wavelength_t.ibw"))
            wav_t = wav_t['wave']['wData']
    except:
            dual_pol = False
    
    # displacement, conductance and force #
    disp = loadibw(os.path.join(target, "displacement.ibw"))
    disp = disp['wave']['wData']
    current = loadibw(os.path.join(target, "current.ibw"))
    current = current['wave']['wData']
    cond = loadibw(os.path.join(target, "conductance.ibw"))
    cond = cond['wave']['wData']
    psd_y = loadibw(os.path.join(target, "psd_y.ibw"))
    psd_y = psd_y['wave']['wData']
    psd_x = loadibw(os.path.join(target, "psd_x.ibw"))
    psd_x = psd_x['wave']['wData']
    
    # parameters #
##  params = load_params(target)
    scan_n = int(os.path.basename(target).rsplit("_", 1)[1])

    # isolate spectral region of interest #
    wav = np.array(wav)
    disp = 1000 * (disp - disp[0])
    wl_l = wavelength_to_index(500e-9, wav)
    wl_u = wavelength_to_index(900e-9, wav)
    wav = wav[wl_l:wl_u]
    spec2d = spec2d[:, wl_l:wl_u]
    energy = make_energy_array(wav)

    if dual_pol == True:
            wl_l = wavelength_to_index(500e-9, wav_t)
            wl_u = wavelength_to_index(900e-9, wav_t)
            wav_t = wav_t[wl_l:wl_u]
            spec2d_t = spec2d_t[:, wl_l:wl_u]
            energy_t = make_energy_array(wav_t)

    ## pre-plot analysis ##
    # find StoC #
    grad = np.gradient(psd_y)
    stoc = np.argmin(grad)
    print "StoC =", stoc

    # Set up the figure #
    if dual_pol == True:
        fig_width_cm = 35.0
    else:
        fig_width_cm = 25.0
    inches_per_cm = 1.0/2.54
    fig_width = fig_width_cm * inches_per_cm
    fig_height = 0.5 * fig_width
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
    fig = plt.figure()


    if dual_pol == True:
            gs0 = gridspec.GridSpec(1, 3, width_ratios=[0.75,1,1])
            spec_ax = 132
            spec_ax = plt.Subplot(fig, gs0[0, 1])
            spect_ax = 133
            spect_ax = plt.Subplot(fig, gs0[0, 2], sharex=spec_ax)
    else:
            gs0 = gridspec.GridSpec(1, 2, width_ratios=[0.75,1])
            spec_ax = 122
            spec_ax = plt.Subplot(fig, gs0[0, 1])

    gs00 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs0[0])
    disp_ax = plt.Subplot(fig, gs00[0, 0], sharey=spec_ax)
    cond_ax = plt.Subplot(fig, gs00[0, 2], sharey=spec_ax)
    f_ax = plt.Subplot(fig, gs00[0, 1], sharey=spec_ax)    

    ## plot data ##
    # spec subplot #
    add_spec_subplot(fig, spec_ax, spec2d, 'spec',
                     xwave=energy, ywave=None,
                     xname='energy (eV)', yname='')
    if dual_pol == True:
            # spec_t subplot
            add_spec_subplot(fig, spect_ax, spec2d_t, 'spec_t',
                             xwave=energy_t, ywave=None,
                             xname='energy (eV)', yname='')
    # add other plots #
    add_cond_subplot(fig, cond_ax, cond, current)
    add_force_subplot(fig, f_ax, psd_x, psd_y)
    add_disp_subplot(fig, disp_ax, disp)

    # annotate plots #
    spec_ax.axhline(y=stoc, c='k', ls='--')
    if dual_pol == True:
        spect_ax.axhline(y=stoc, c='k', ls='--')
    cond_ax.axhline(y=stoc, c='k', ls='--')
    f_ax.axhline(y=stoc, c='k', ls='--')
    disp_ax.axhline(y=stoc, c='k', ls='--')

    #plt.tight_layout()
    gs0.tight_layout(fig, pad=0.25)#, w_pad=0.1, h_pad=0.1)

    # save figure #
    save_fig(fig, "tip_scan_" + str(scan_n), target)

    # check for any time-resolved measurements to plot #
    tr_data_path = os.path.join(target, "time_resolved_data")
    tr_scans = [(x.rsplit("_", 1)[1]).split(".",1)[0] for x in os.listdir(tr_data_path)
               if "qc_spec" in x and ".ibw" in x]
    #print tr_scans
    for instance in tr_scans:
        display_time_resolved_experiment_scan(target, instance)

    return 0

################################################################################

if __name__ == "__main__":
    init_target = get_host_data_folder()
    mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    day = raw_input("Enter day (dd): ")
    scan_n = raw_input("Enter scan: ")
    target = os.path.join(init_target, str(mon_yr))
    target = os.path.join(target, "day_" + str(day))
    target = os.path.join(target, "tip_exp_" + str(scan_n))
    display_experiment_scan(target)
    plt.show()

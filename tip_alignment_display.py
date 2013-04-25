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

def add_subplot(X, Y, wave, name, fig, ax1, ax2, formatter):
    wave = ndimage.gaussian_filter(wave, 0.7)
    Z = wave

    x_offset = 0.5*(X.max()-X.min())
    y_offset = 0.5*(Y.max()-Y.min())
    z_offset = 0.75*(Z.max()-Z.min())

    c_levels = np.linspace(Z.min(), 1.05*Z.max(), 50)
    l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
    cmap = cm.Spectral_r
    norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
    lw = 0.5
    
    ax = fig.add_subplot(ax1, projection='3d')
    ax.plot_surface(X, Y, Z, c_levels, rstride=1, cstride=1, linewidth=0.2, alpha=1.0,
                    #antialiased=False,
                    norm=norm,
                    cmap=cm.get_cmap(cmap, len(c_levels)-1))
    #ax.plot_trisurf(X, Y, Z, linewidth=0.2, cmap=cm.get_cmap(cmap))
    ax.view_init(elev=25.0, azim=-45.0)
    #z
    cset = ax.contourf(X, Y, Z, c_levels,
                       zdir='z', offset=Z.min()-z_offset,
                       norm=norm,
                       alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    cset = ax.contour(X, Y, Z, l_levels,
                      zdir='z', offset=Z.min()-z_offset,
                      #norm=norm,
                      linewidths=lw, colors='k', linestyles='solid')
    #x
    cset = ax.contourf(X, Y, Z,# c_levels,
                       zdir='x', offset=X.min()-x_offset,
                       #interpolation='nearest',
                       #norm=norm,
                       alpha=0.5, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    cset = ax.contour(X, Y, Z,# l_levels,
                      zdir='x', offset=X.min()-x_offset,
                      #norm=norm,
                      linewidths=lw, colors='k', linestyles='solid')
    #y
    cset = ax.contourf(X, Y, Z,# c_levels,
                       zdir='y', offset=Y.max()+y_offset,
                       #norm=norm,
                       alpha=0.5, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    cset = ax.contour(X, Y, Z,# l_levels,
                      zdir='y', offset=Y.max()+y_offset,
                      #norm=norm,
                      linewidths=lw, colors='k', linestyles='solid')

    ax.xaxis.set_major_formatter(formatter) 
    ax.yaxis.set_major_formatter(formatter)
    ax.zaxis.set_major_formatter(formatter)
    
    ax.set_xlim(X.min()-x_offset, X.max())
    ax.set_ylim(Y.min(), Y.max()+y_offset)
    ax.set_zlim(Z.min()-z_offset, Z.max())
    ax.set_xlabel(r'position ($\mu$m)')
    ax.set_ylabel(r'position ($\mu$m)')
    if ax1 == 231:#x_ax:
        ax.set_zlabel(r'$V_x$ ($\mu$V)', labelpad=30, linespacing=2)
        ax.zaxis.labelpad=30
    elif ax1 == 234:#y_ax:
        ax.set_zlabel(r'$V_y$ ($\mu$V)')
    elif ax1 == 232:#r_ax:
        ax.set_zlabel(r'$I_{3\omega_s}$ (A)')
    elif ax1 == 235:#theta_ax:
        ax.set_zlabel(r'$\theta$ ($\degree$)')
    elif ax1 == 233:#psd_ax:
        ax.set_zlabel(r'$V_{pk-pk}$ (V)')

    x2, y2, _ = proj3d.proj_transform(1,1,1, ax.get_proj())
    label = ax.annotate(name,
                        xy = (0, 0), xytext = (-150, 100),
                        textcoords = 'offset points', ha = 'right', va = 'bottom',
                        color='black', fontsize=12, fontweight='bold')
    
    # extra plot
    ax = fig.add_subplot(ax2)
    cset = ax.contourf(X, Y, Z, c_levels,
                       norm=norm,
                       alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    cset = ax.contour(X, Y, Z, l_levels,
                      #norm=norm,
                      linewidths=lw, colors='k', linestyles='solid')
    ax.text(0.05, 0.95, name, ha='left', va='top', color='white',
            fontsize=12, fontweight='bold', transform=ax.transAxes)
    if ax1 == 231:#x_ax2:
        ax.set_xticklabels(ax.get_xticklabels(), visible=False)
        ax.set_ylabel(r'position ($\mu$m)')
    elif ax1 == 234:#y_ax2:
        ax.set_xlabel(r'position ($\mu$m)')
        ax.set_ylabel(r'position ($\mu$m)')
    elif ax1 == 232:#r_ax2:
        ax.set_xticklabels(ax.get_xticklabels(), visible=False)
        ax.set_yticklabels(ax.get_yticklabels(), visible=False)
    elif ax1 == 235:#theta_ax2:
        ax.set_yticklabels(ax.get_yticklabels(), visible=False)
        ax.set_xlabel(r'position ($\mu$m)')
    elif ax1 == 233:#psd_ax2:
        ax.set_yticklabels(ax.get_yticklabels(), visible=False)
        ax.set_xlabel(r'position ($\mu$m)')
    return 0

def add_subplot2(X, Y, wave, name, fig, ax):
    wave = ndimage.gaussian_filter(wave, 0.7)
    Z = wave

    ax.set_xlim(X.min(), X.max())
    ax.set_ylim(Y.min(), Y.max())

    c_levels = np.linspace(Z.min(), 1.05*Z.max(), 50)
    l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
    cmap = cm.Spectral_r
    norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
    lw = 0.5
    #cax = ax2.imshow(Z, vmin=Z.min(), vmax=Z.max(),
    #                origin='lower', aspect='auto', cmap=cm.get_cmap(m))
    cfax = ax.contourf(X, Y, Z, c_levels,
                       norm=norm,
                       alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    cax = ax.contour(X, Y, Z, l_levels,
                      #norm=norm,
                      linewidths=lw, colors='k', linestyles='solid')
    ax.text(0.05, 0.95, name, ha='left', va='top', color='white',
            fontsize=12, fontweight='bold', transform=ax.transAxes)
    return 0

def display_alignment_scan(target):
    # load parameters inforamtion
    params = load_params(target)

    # extract alignment data - requires fixing
    #scan_n = int(os.path.dirname(target).rsplit("_", 1)[1])
    scan_n = int(os.path.basename(target).rsplit("_", 1)[1])
    scan_size = params['scan_size']
    scan_step = params['scan_step']
    frequency = params['frequency']
    voltage = params['voltage']
    offset = params['offset']
    init_pos_a = params['init_pos_a']
    init_pos_b = params['init_pos_b']
    init_pos_c = params['init_pos_c']
    time_stamp = params['time_stamp']
    try:
        alignment_set = params['alignment_set']
    except KeyError:
        alignment_set = 0
    try:
        x0 = params['x0']
        y0 = params['y0']
    except KeyError:
        x0 = 'n/a'
        y0 = 'n/a'
    try:
        electronic_alignment = params['electronic_alignment']
    except KeyError:
        electronic_alignment = 1
    try:
        force_alignment = params['force_alignment']
    except KeyError:
        force_alignment = 0

    if electronic_alignment == 1:
        # load required data in target folder
        x_data = loadibw(os.path.join(target, "alignment_scan_x.ibw"))
        x_wdata = x_data['wave']['wData']
        x_wdata = x_wdata.T
        y_data = loadibw(os.path.join(target, "alignment_scan_y.ibw"))
        y_wdata = y_data['wave']['wData']
        y_wdata = y_wdata.T
        r_data = loadibw(os.path.join(target, "alignment_scan_r.ibw"))
        r_wdata = r_data['wave']['wData']
        r_wdata = r_wdata.T
        theta_data = loadibw(os.path.join(target, "alignment_scan_theta.ibw"))
        theta_wdata = theta_data['wave']['wData']
        theta_wdata = theta_wdata.T
        psd_data = loadibw(os.path.join(target, "alignment_scan_y_psd.ibw"))
        psd_wdata = psd_data['wave']['wData']
        psd_wdata = psd_wdata.T
    if force_alignment == 1:
        fx_data = loadibw(os.path.join(target, "alignment_scan_fx.ibw"))
        fx_wdata = fx_data['wave']['wData']
        fx_wdata = fx_wdata.T
        fy_data = loadibw(os.path.join(target, "alignment_scan_fy.ibw"))
        fy_wdata = fy_data['wave']['wData']
        fy_wdata = fy_wdata.T
        fr_data = loadibw(os.path.join(target, "alignment_scan_fr.ibw"))
        fr_wdata = fr_data['wave']['wData']
        fr_wdata = fr_wdata.T
        ftheta_data = loadibw(os.path.join(target, "alignment_scan_ftheta.ibw"))
        ftheta_wdata = ftheta_data['wave']['wData']
        ftheta_wdata = ftheta_wdata.T

    # create X and Y waves for alignment plots #
    if force_alignment:
        Z = fr_wdata
    else:
        Z = r_wdata
    step = float(params['scan_step'])
    X = step * np.linspace(-Z.shape[1]/2, Z.shape[1]/2, Z.shape[1])
    Y = step * np.linspace(-Z.shape[0]/2, Z.shape[0]/2, Z.shape[0])
    X, Y = np.meshgrid(X, Y)

    # Set up the figure
    fig_width_cm = 40.0
    inches_per_cm = 1.0/2.54
    fig_width = fig_width_cm * inches_per_cm
    fig_height = 0.5 * fig_width
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

    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))

    plt.close('all')
    fig = plt.figure()
    gs0 = gridspec.GridSpec(2, 3)    
    gs00 = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec=gs0[5])
    if electronic_alignment == 1 and force_alignment == 0:
        x_ax = 231
        y_ax = 234
        r_ax = 232
        theta_ax = 235
        psd_ax = 233
        x_ax2 = plt.Subplot(fig, gs00[0, 0])
        y_ax2 = plt.Subplot(fig, gs00[1, 0])#, sharex=x_ax2, sharey=x_ax2)
        r_ax2 = plt.Subplot(fig, gs00[0, 1])#, sharex=x_ax2, sharey=x_ax2)
        theta_ax2 = plt.Subplot(fig, gs00[1, 1])#, sharex=x_ax2, sharey=x_ax2)
        psd_ax2 = plt.Subplot(fig, gs00[0, 2])#, sharex=x_ax2, sharey=x_ax2)
        # subplots
        add_subplot(X, Y, x_wdata, "X", fig, x_ax, x_ax2, formatter)
        add_subplot(X, Y, y_wdata, "Y", fig, y_ax, y_ax2, formatter)
        add_subplot(X, Y, r_wdata, "R", fig, r_ax, r_ax2, formatter)
        add_subplot(X, Y, theta_wdata, r"$\theta$", fig, theta_ax, theta_ax2, formatter)
        add_subplot(X, Y, psd_wdata, "PSD", fig, psd_ax, psd_ax2, formatter)
    elif electronic_alignment == 1 and force_alignment == 1:
        r_ax = 231
        theta_ax = 234
        fr_ax = 232
        ftheta_ax = 235
        psd_ax = 233
        r_ax2 = plt.Subplot(fig, gs00[0, 0])
        theta_ax2 = plt.Subplot(fig, gs00[1, 0])#, sharex=x_ax2, sharey=x_ax2)
        fr_ax2 = plt.Subplot(fig, gs00[0, 1])#, sharex=x_ax2, sharey=x_ax2)
        ftheta_ax2 = plt.Subplot(fig, gs00[1, 1])#, sharex=x_ax2, sharey=x_ax2)
        psd_ax2 = plt.Subplot(fig, gs00[0, 2])#, sharex=x_ax2, sharey=x_ax2)
        # subplots
        add_subplot(X, Y, r_wdata, "R", fig, r_ax, r_ax2, formatter)
        add_subplot(X, Y, theta_wdata, r"$\theta$", fig, theta_ax, theta_ax2, formatter)
        add_subplot(X, Y, fr_wdata, "$F_r$", fig, fr_ax, fr_ax2, formatter)
        add_subplot(X, Y, ftheta_wdata, r"$F_\theta$", fig, ftheta_ax, ftheta_ax2, formatter)
        add_subplot(X, Y, psd_wdata, "PSD", fig, psd_ax, psd_ax2, formatter)
    param_ax = plt.Subplot(fig, gs00[1,2])

    # param display
    ax = fig.add_subplot(param_ax)
    ax.text(0.1, 0.7,
            "scan # = %d\n"\
            "set # = %d\n"\
            "time = %s\n"\
            "scan size = %s\n"\
            "scan step = %s\n"\
            "voltage = %s\n"\
            "pos_a = %s\n"\
            "x0 = %s\n"\
            "y0 = %s\n"\
            %(scan_n, alignment_set, time_stamp, scan_size, scan_step, voltage,
              init_pos_a, x0, y0),
            va="top", ha="left", fontsize=10.0)
    ax.set_axis_off()

    plt.tight_layout(pad=0.25)#, w_pad=0.1, h_pad=0.1)
    save_fig(fig, "alignment_scan_" + str(scan_n), target)

    # second figure
    if electronic_alignment == 1 and force_alignment == 0:
        fig_width_cm = 15.0
        inches_per_cm = 1.0/2.54
        fig_width = fig_width_cm * inches_per_cm
        fig_height = 0.67 * fig_width
    else:
        fig_width_cm = 20.0
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
              'figure.subplot.wspace' : 0.02,
              'figure.subplot.hspace' : 0.02,
              'figure.figsize': fig_size}
    plt.rcParams.update(params)

    if electronic_alignment == 1 and force_alignment == 0:
        fig, ((x_ax2, r_ax2, psd_ax2), (y_ax2, theta_ax2, param_ax)) = plt.subplots(2, 3, sharex='all', sharey='all')
    elif electronic_alignment == 1 and force_alignment == 1:
        fig, ((x_ax2, y_ax2, r_ax2, theta_ax2),
              (fx_ax2, fy_ax2, fr_ax2, ftheta_ax2),
              (psd_ax2, param_ax, free_ax1, free_ax2)) = plt.subplots(3, 4, sharex='all', sharey='all')

    #fig = plt.figure()
    #x_ax2 = fig.add_subplot(231)
    #y_ax2 = fig.add_subplot(234, sharex=x_ax2)
    #r_ax2 = fig.add_subplot(232, sharey=x_ax2)
    #theta_ax2 = fig.add_subplot(235, sharex=r_ax2, sharey=y_ax2)
    #psd_ax2 = fig.add_subplot(233, sharey=x_ax2)
    #param_ax = fig.add_subplot(236)

    # electronic signal subplot
    if electronic_alignment == 1:
        add_subplot2(X, Y, x_wdata, "X", fig, x_ax2)
        add_subplot2(X, Y, y_wdata, "Y", fig, y_ax2)
        add_subplot2(X, Y, r_wdata, "R", fig, r_ax2)
        add_subplot2(X, Y, theta_wdata, r"$\theta$", fig, theta_ax2)
    # psd subplot
    add_subplot2(X, Y, psd_wdata, "PSD", fig, psd_ax2)
    #force subplot
    if force_alignment == 1:
        add_subplot2(X, Y, fx_wdata, "$F_x$", fig, fx_ax2)
        add_subplot2(X, Y, fy_wdata, "$F_y$", fig, fy_ax2)
        add_subplot2(X, Y, fr_wdata, "$F_r$", fig, fr_ax2)
        add_subplot2(X, Y, ftheta_wdata, r"$F_\theta$", fig, ftheta_ax2)
    # param display
    param_ax.text(0.1, 0.9,
                  "scan # = %d\n"\
                  "set # = %d\n"\
                  "time = %s\n"\
                  "scan size = %s\n"\
                  "scan step = %s\n"\
                  "voltage = %s\n"\
                  "pos_a = %s\n"\
                  "x0 = %s\n"\
                  "y0 = %s\n"\
                  %(scan_n, alignment_set, time_stamp, scan_size, scan_step,
                    voltage, init_pos_a, x0, y0),
                  va="top", ha="left", transform=param_ax.transAxes, fontsize=10.0)
    param_ax.set_axis_off()

    if force_alignment == 1:
        free_ax1.set_axis_off()
        free_ax2.set_axis_off()

    psd_ax2.set_xlabel(r'position ($\mu$m)')
    fx_ax2.set_ylabel(r'position ($\mu$m)')

    plt.tight_layout(pad=0.25)
    #gs0.tight_layout(fig)
    save_fig(fig, "alignment_scan_" + str(scan_n) + "_2", target)

    return 0

if __name__ == "__main__":
    init_target = get_host_data_folder()
    mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    day = raw_input("Enter day (dd): ")
    scan_n = raw_input("Enter scan: ")
    target = os.path.join(init_target, str(mon_yr))
    target = os.path.join(target, "day_" + str(day))
    target = os.path.join(target, "alignment_scans")
    target = os.path.join(target, "scan_" + str(scan_n))
    display_alignment_scan(target)
    plt.show()

import os
import sys
file_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
root_dir = os.path.dirname(file_dir)
# load computer definitions and data handling #
#module_dir = os.path.join(root_dir, "igor-pro-tools")
#if module_dir not in sys.path:
#	sys.path.append(module_dir)
#from data_handling import *
from data_classes import *
import numpy as np
# load matplotlib modules #
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

class spatial_figure:
    def __init__(self, spatial_data):
        self.data = spatial_data
        # figure setup #
        self.setup_figure()
        self.fig = plt.figure()
        # setup subplots #
        if self.data.dual_pol:
            self.gs0 = gridspec.GridSpec(1, 3, width_ratios=[0.75,1,1])
            self.spectra_long_ax = plt.Subplot(self.fig, self.gs0[0, 1])
            self.spectra_trans_ax = plt.Subplot(self.fig, self.gs0[0, 2], sharex=self.spectra_long_ax, sharey=self.spectra_long_ax)
        else:
            self.gs0 = gridspec.GridSpec(1, 2, width_ratios=[0.75,1])
            self.spectra_long_ax = plt.Subplot(self.fig, self.gs0[0, 1])
        self.gs00 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=self.gs0[0,0])
        self.conductance_ax = plt.Subplot(self.fig, self.gs00[0, 2], sharey=self.spectra_long_ax)
        self.current_ax = 0
        self.force_y_ax = plt.Subplot(self.fig, self.gs00[0, 1], sharey=self.spectra_long_ax)
        self.force_x_ax = 0
        self.displacement_ax = plt.Subplot(self.fig, self.gs00[0, 0], sharey=self.spectra_long_ax)
        # set axis formatter #
        self.formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
        self.formatter.set_scientific(True) 
        self.formatter.set_powerlimits((-3,3))
        # add subplots #
        self.add_spectra_subplot()
        self.add_conductance_subplot()
        self.add_force_subplot()
        self.add_displacement_subplot()
        #plt.tight_layout()
        self.gs0.tight_layout(self.fig, pad=0.25)#, w_pad=0.1, h_pad=0.1)
        
        if self.data.analysed: self.annotate_analysis() # annotate analysis
        self.save_figure() # save figure
    
    def setup_figure(self):
        if self.data.dual_pol: fig_width_cm = 35.0
        else: fig_width_cm = 25.0
        inches_per_cm = 1.0/2.54
        fig_width = fig_width_cm * inches_per_cm
        fig_height = 0.75 * fig_width
        fig_size = (fig_width, fig_height)
        params = {'backend': 'ps',
                'axes.labelsize': 10,
                'text.fontsize': 11,
                'legend.fontsize': 10,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'text.usetex': False,
                'figure.subplot.left' : 0.01,
                'figure.subplot.bottom' : 0.01,
                'figure.subplot.right' : 0.99,
                'figure.subplot.top' : 0.99,
                'figure.subplot.wspace' : 0.04,
                'figure.subplot.hspace' : 0.00,
                'figure.figsize': fig_size}
        plt.rcParams.update(params)
    
    def save_figure(self):
        # identify day folder #
        data_loc = self.data.location
        fig_folder = os.path.dirname(data_loc)
        while "day" not in os.path.basename(fig_folder):
            fig_folder = os.path.dirname(fig_folder)
        # save figure to day folder #
        fname = os.path.join(fig_folder, "tip_scan_" + str(self.data.scan_n))
        #print "saving figure to", fname, ".png"
        plt.savefig(fname + '.png', bbox_inches=0)
    
    def format_axes(self, ax, ax_id):
        # common formatting #
        ax.minorticks_on()
        # specific formatting #
        if ax_id == 'spectra_long' or ax_id == 'spectra_trans':
            ax.xaxis.set_major_formatter(self.formatter)
            #ax.set_autoscale_on(False)
            ax.set_ylim(self.data.step.min(), self.data.step.max())
            ax.set_xlabel("wavelength (m)")
        if ax_id == 'spectra_long':
            ax.set_ylabel("step (nm)")
        if ax_id == 'spectra_trans':
            for label in ax.get_yticklabels(): label.set_visible(False)
        # supplementary axes #
        if ax_id == 'current' or ax_id == 'conductance'\
        or ax_id == 'force_x' or ax_id == 'force_y' or ax_id == 'displacement':
            loc = ax.xaxis.get_major_locator()
            loc.numticks = 5
            ax.invert_xaxis()
            for label in ax.get_xticklabels(): label.set_rotation(90)
        # specifics #
        if ax_id == 'current':
            ax.set_xscale('log')
            x_range = self.data.current.max() - self.data.current.min()
            ax.set_xlim(self.data.current.min() - 0.05*x_range, self.data.current.max()+ 0.05*x_range)
            ax.set_xlabel("$I (A)$")
        elif ax_id == 'conductance':
            ax.set_xscale('log')
            x_range = self.data.conductance.max() - self.data.conductance.min()
            ax.set_xlim(self.data.conductance.min() - 0.05*x_range, self.data.conductance.max()+ 0.05*x_range)
            ax.set_xlabel("$G$ ($G_0$)")
            for label in ax.get_yticklabels(): label.set_visible(False)
            ax.set_ylim(self.data.step.min(), self.data.step.max())
        elif ax_id == 'force_x':
            x_range = self.data.force_x.max() - self.data.force_x.min()
            ax.set_xlim(self.data.force_x.min() - 0.05*x_range, self.data.force_x.max()+ 0.05*x_range)
            ax.set_xlabel("$V_{x,psd}$ (V)")
            ax.xaxis.set_major_locator(MaxNLocator(5))
        elif ax_id == 'force_y':
            x_range = self.data.force_y.max() - self.data.force_y.min()
            ax.set_xlim(self.data.force_y.min() - 0.05*x_range, self.data.force_y.max()+ 0.05*x_range)
            ax.set_xlabel("$V_{y,psd}$ (V)")
            for label in ax.get_yticklabels(): label.set_visible(False)
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.set_ylim(self.data.step.min(), self.data.step.max())
        elif ax_id == 'displacement':
            x_range = self.data.displacement.max() - self.data.displacement.min()
            ax.set_xlim(self.data.displacement.min() - 0.05*x_range, self.data.displacement.max()+ 0.05*x_range)
            ax.set_xlabel("$z_{PZ}$ (nm)")
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.xaxis.set_major_formatter(self.formatter) 
            #self.displacement_ax.yaxis.set_major_formatter(self.formatter)
            # set step axis for whole figure #
            ax.set_ylim(self.data.step.min(), self.data.step.max())
            ax.set_ylabel("step (nm)")
        
    def annotate_analysis(self):
        self.spectra_long_ax.axhline(y=self.data.stoc, c='k', ls='--')
        if self.data.dual_pol: self.spectra_trans_ax.axhline(y=self.data.stoc, c='k', ls='--')
        self.conductance_ax.axhline(y=self.data.stoc, c='k', ls='--')
        self.force_y_ax.axhline(y=self.data.stoc, c='k', ls='--')
        self.displacement_ax.axhline(y=self.data.stoc, c='k', ls='--')
    
    def add_spectra_subplot(self):
        # get spectra data #
        Zl = self.data.spectra_long
        Xl = self.data.wavelength_long
        Yi = self.data.step
        minimum = Zl.min()
        maximum = Zl.max()
        if self.data.dual_pol:
            Zt = self.data.spectra_trans
            Xt = self.data.wavelength_trans
            minimum = Zl.min() if Zl.min() < Zt.min() else Zt.min()
            maximum = Zl.max() if Zl.max() > Zt.max() else Zt.max()
        # set colour mapping for all axes #
        c_levels = np.linspace(minimum, 1.05*maximum, 100)
        cmap = cm.Spectral_r
        norm = cm.colors.Normalize(vmax=maximum, vmin=minimum)
        lw = 0.5
        
        # create longitudinal spectral image subplot #
        Xl, Y = np.meshgrid(Xl, Yi)
        self.spectra_long_ax = self.fig.add_subplot(self.spectra_long_ax)
        cfax = self.spectra_long_ax.contourf(Xl, Y, Zl, c_levels,
                                             norm=norm,
                                             alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
        self.format_axes(self.spectra_long_ax, 'spectra_long') # format axes
        
        if self.data.dual_pol:
            # create transverse spectral image subplot #
            Xt, Y = np.meshgrid(Xt, Yi)
            self.spectra_trans_ax = self.fig.add_subplot(self.spectra_trans_ax)
            cfax = self.spectra_trans_ax.contourf(Xt, Y, Zt, c_levels,
                                                  norm=norm,
                                                  alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
            self.format_axes(self.spectra_trans_ax, 'spectra_trans') # format axes
        
        # add colour bar to far right of figure #
        cb = plt.colorbar(cfax, shrink=0.75, extend='both')
        cb.set_label('optical scattering (a.u.)')
        return 0    
                
    def add_conductance_subplot(self):
        # conductance #
        self.conductance_ax = self.fig.add_subplot(self.conductance_ax)
        self.conductance_ax.plot(self.data.conductance, self.data.step, 'k-')
        self.format_axes(self.conductance_ax, 'conductance')
        # current #
        self.current_ax = self.conductance_ax.twiny()
        self.current_ax.plot(self.data.current, self.data.step, 'k-')
        self.format_axes(self.current_ax, 'current')
        return 0
        
    def add_force_subplot(self):
        # lateral force #
        self.force_y_ax = self.fig.add_subplot(self.force_y_ax)
        self.force_y_ax.plot(self.data.force_y, self.data.step, 'r-')
        self.format_axes(self.force_y_ax, 'force_y')
        # torsional force #
        self.force_x_ax = self.force_y_ax.twiny()
        self.force_x_ax.plot(self.data.force_x, self.data.step, 'b-')
        self.format_axes(self.force_x_ax, 'force_x')
        return 0
    
    def add_displacement_subplot(self):
        # displacement
        # lateral force #
        self.displacement_ax = self.fig.add_subplot(self.displacement_ax)
        self.displacement_ax.plot(self.data.displacement, self.data.step, 'k-')
        self.format_axes(self.displacement_ax, 'displacement')
        return 0

class temporal_figure:
    def __init__(self, temporal_data):
        self.data = temporal_data
        # figure setup #
        self.setup_figure()
        self.fig = plt.figure()
        # setup subplots #
        self.gs0 = gridspec.GridSpec(1, 2)
        self.spectra_ax = plt.Subplot(self.fig, self.gs0[0, 1])
        self.gs00 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=self.gs0[0,0])
        self.conductance_ax = plt.Subplot(self.fig, self.gs00[0, 1], sharey=self.spectra_ax)
        self.current_ax = 0
        self.force_ax = plt.Subplot(self.fig, self.gs00[0, 0], sharey=self.spectra_ax)
        # set axis formatter #
        self.formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
        self.formatter.set_scientific(True) 
        self.formatter.set_powerlimits((-3,3))
        # add subplots #
        self.add_spectra_subplot()
        self.add_conductance_subplot()
        self.add_force_subplot()
        #plt.tight_layout()
        self.gs0.tight_layout(self.fig, pad=0.25)#, w_pad=0.1, h_pad=0.1)
        self.save_figure()
        
    def setup_figure(self):
        fig_width_cm = 25.0
        inches_per_cm = 1.0/2.54
        fig_width = fig_width_cm * inches_per_cm
        fig_height = 0.75 * fig_width
        fig_size = (fig_width, fig_height)
        params = {'backend': 'ps',
                'axes.labelsize': 10,
                'text.fontsize': 11,
                'legend.fontsize': 10,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'text.usetex': False,
                'figure.subplot.left' : 0.01,
                'figure.subplot.bottom' : 0.01,
                'figure.subplot.right' : 0.99,
                'figure.subplot.top' : 0.99,
                'figure.subplot.wspace' : 0.04,
                'figure.subplot.hspace' : 0.00,
                'figure.figsize': fig_size}
        plt.rcParams.update(params)
    
    def save_figure(self):
        # identify day folder #
        data_loc = self.data.location
        fig_folder = os.path.dirname(data_loc)
        while "day" not in os.path.basename(fig_folder):
            fig_folder = os.path.dirname(fig_folder)
        # save figure to day folder #
        fname = os.path.join(fig_folder, "tip_scan_" + str(self.data.scan_n) + "_tr_" + str(self.data.instance))
        #print "saving figure to", fname, ".png"
        plt.savefig(fname + '.png', bbox_inches=0)
    
    def format_axes(self, ax, ax_id):
        # common formatting #
        #ax.minorticks_on()
        # specific formatting #
        if ax_id == 'spectra':
            ax.set_ylim(self.data.spectra_time.min(), self.data.spectra_time.max())
            for label in ax.get_yticklabels(): label.set_visible(False)
            ax.set_xlabel("wavelength (m)")
            #self.spectra_ax.set_ylabel("time (s)")
            ax.xaxis.set_major_formatter(self.formatter)
            ax.minorticks_on()
        # supplementary axes #
        elif ax_id == 'conductance':
            # set axis ticks #
            loc = ax.xaxis.get_major_locator()
            loc.numticks = 5
            x_range = self.data.conductance.max() - self.data.conductance.min()
            ax.set_xlim(self.data.conductance.min() - 0.05*x_range, self.data.conductance.max()+ 0.05*x_range)
            ax.invert_xaxis()
            # format axes #
            ax.set_ylim(self.data.dso_time.min(), self.data.dso_time.max())
            ax.set_xlabel("$G$ ($G_0$)")
            for label in ax.get_xticklabels(): label.set_rotation(90)
            for label in ax.get_yticklabels(): label.set_visible(False)
        elif ax_id == 'current':
            # set axis ticks #
            loc = self.current_ax.xaxis.get_major_locator()
            loc.numticks = 5
            x_range = self.data.current.max() - self.data.current.min()
            ax.set_xlim(self.data.current.min() - 0.05*x_range, self.data.current.max()+ 0.05*x_range)
            ax.invert_xaxis()
            # format axes #
            ax.set_xlabel("$I (A)$")
            for label in ax.get_xticklabels(): label.set_rotation(90)
        elif ax_id == 'force':
            # set axis ticks #
            loc = ax.xaxis.get_major_locator()
            loc.numticks = 2
            x_range = self.data.force_y.max() - self.data.force_y.min()
            ax.set_xlim(self.data.force_y.min() - 0.05*x_range, self.data.force_y.max() + 0.05*x_range)
            ax.invert_xaxis()
            # format axes #
            ax.set_ylim(self.data.dso_time.min(), self.data.dso_time.max())
            ax.set_xlabel("$V_{y,psd}$ (V)")
            for label in ax.get_xticklabels(): label.set_rotation(90)
            ax.xaxis.set_major_locator(MaxNLocator(5))
            ax.xaxis.set_major_formatter(self.formatter)
            # format time axis (representative for all related subplots) # 
            ax.yaxis.set_major_formatter(self.formatter)
            ax.set_ylabel("time (s)")
    
    def add_spectra_subplot(self):
        # setup data for plot #
        Z = self.data.spectra_long.T
        Xi = self.data.wavelength_long
        Yi = self.data.spectra_time
        print Xi.shape, Yi.shape, Z.shape
        X, Y = np.meshgrid(Xi, Yi)
        print X.shape, Y.shape, Z.shape
        # setup display attributes #
        c_levels = np.linspace(Z.min(), 1.05*Z.max(), 100)
        cmap = cm.Spectral_r
        norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
        lw = 0.5
        # plot spectral image in subplot #
        self.spectra_ax = self.fig.add_subplot(self.spectra_ax)
        cfax = self.spectra_ax.contourf(X, Y, Z, c_levels,
                                        norm=norm,
                                        alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
        # format axes #
        self.format_axes(self.spectra_ax, 'spectra')
        cb = plt.colorbar(cfax, shrink=1.0, extend='both')
        cb.set_label('optical scattering (a.u.)')
        return 0
    
    def add_conductance_subplot(self):
        # plot conductance data in subplot #
        self.conductance_ax = self.fig.add_subplot(self.conductance_ax)
        self.conductance_ax.plot(self.data.conductance, self.data.dso_time, 'k-')
        self.format_axes(self.conductance_ax, 'conductance')
        # plot current data on opposite subplot axis #
        self.current_ax = self.conductance_ax.twiny()
        self.current_ax.plot(self.data.current, self.data.dso_time, 'k-')
        self.format_axes(self.current_ax, 'current')
        return 0
    
    def add_force_subplot(self):
        # plot lateral force data in subplot #
        self.force_ax = self.fig.add_subplot(self.force_ax)
        self.force_ax.plot(self.data.force_y, self.data.dso_time, 'r-')
        self.format_axes(self.force_ax, 'force')
        return 0

if __name__ == '__main__':
    location = 'C:\\users\\alan\\skydrive\\documents\\phd\\0 - experiment\\data\\raw data\\aug_2013\\day_07\\tip_exp_1'
    #data = spatial_data(location)
    #data.set_wavelength_roi(450e-9, 900e-9)
    #data.set_step_roi(0, 220)
    #data.smooth_spectra()
    #data.analyse_data()
    #sfig = spatial_figure(data)
    instance = '158'
    data = temporal_data(location, instance)
    print data.spectra_long.shape, data.wavelength_long.shape, data.spectra_time.shape
    data.set_wavelength_roi(450e-9, 800e-9)
    print data.spectra_long.shape, data.wavelength_long.shape, data.spectra_time.shape
    tfig = temporal_figure(data)
    plt.show()
from library.data_classes.alignment_data_classes import *
from library.publication_figures import *
from scipy import ndimage
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gridspec
import numpy as np

def alignment_subplot_3d():
    return 0

class alignment_plot:
    def __init__(self, location):
        self.location = location
        # initialise figure #    
        self.fig = plt.figure()
        self.update_figure()
        self.set_formatter()
        # create parameters subplot #
        params = load_parameters(location)
        # get data #
        # setup subplots #
    
    def update_figure(self):
        fig_width_cm = 8.0
        inches_per_cm = 1.0/2.54
        fig_width = fig_width_cm * inches_per_cm
        fig_height = 0.55 * fig_width
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
    
    def set_formatter(self):
        formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
        formatter.set_scientific(True) 
        formatter.set_powerlimits((-3,3))
        return formatter
            
class afm_data_plot:
    def __init__(self, location, fig, ax):
        self.location = location
        self.fig = fig
        self.ax = ax
        # get alignment data for given location #
        try:
            self.afm_data_exists = 1
            self.afm_data = afm_alignment_data(location)
        except IOError:
            self.afm_data_exists = 0
        if self.afm_data_exists:
            # smooth data #
            self.afm_data.amplitude = ndimage.gaussian_filter(self.afm_data.amplitude, 0.7)
            self.afm_data.phase = ndimage.gaussian_filter(self.afm_data.phase, 0.7)
            
            # make afm data subplots #
            gs = gridspec.GridSpecFromSubplotSpec(1, 2, self.ax.get_subplotspec(), wspace=0.3)
            r_ax = plt.subplot(gs[0])
            theta_ax = plt.subplot(gs[1])
            # plot on subplot axes #
            self.add_alignment_subplot(self.afm_data.amplitude, r_ax, x=None, y=None, name='$r$')
            self.add_alignment_subplot(self.afm_data.phase, theta_ax, x=None, y=None, name=r'$\theta$')
            for tl in theta_ax.get_yticklabels():
                tl.set_visible(False)
            r_ax.set_ylabel('y position (nm)')
            r_ax.set_xlabel('x position (nm)')
        
    def add_alignment_subplot(self, data, ax, x=None, y=None, name=None):
        size = self.afm_data.scan_size
        step = self.afm_data.scan_step
        if x is None: x = np.arange(-size/2, size/2, step)
        if y is None: y = np.arange(-size/2, size/2, step)
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        x, y = np.meshgrid(x, y)
        c_levels = np.linspace(data.min(), 1.05*data.max(), 50)
        l_levels = np.linspace(data.min(), 1.05*data.max(), 10)
        cmap = cm.Spectral_r
        norm = cm.colors.Normalize(vmax=data.max(), vmin=data.min())
        lw = 0.5
        cfax = ax.contourf(x, y, data, c_levels,
                        norm=norm,
                        alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
        cax = ax.contour(x, y, data, l_levels,
                        norm=norm,
                        linewidths=lw, colors='k', linestyles='solid')
        if name is not None:
            ax.text(0.05, 0.95, name, ha='left', va='top', color='white',
                    fontsize=12, fontweight='bold', transform=ax.transAxes)
        #ax.xaxis.set_major_formatter(self.fig.formatter)
        #ax.yaxis.set_major_formatter(self.fig.formatter)
        return 0
            
if __name__ == '__main__':
    #init_target = get_host_data_folder()
    #mon_yr = raw_input("Enter month_year (mon_yyyy): ")
    #day = raw_input("Enter day (dd): ")
    #scan_n = raw_input("Enter scan: ")
    #target = os.path.join(init_target, str(mon_yr))
    #target = os.path.join(target, "day_" + str(day))
    #target = os.path.join(target, "alignment_scans")
    #target = os.path.join(target, "scan_" + str(scan_n))
    
    fig = publication_figure(aspect=1)
    ax = plt.subplot(211)
    ax.set_xlabel('test')
    ax = plt.subplot(212)
    afm_data_plot('H:\\data\\raw data\\jul_2013\\day_05\\alignment_scans\\scan_13', fig, ax)
    #fig.fig.tight_layout()
    plt.tight_layout()
    plt.show()
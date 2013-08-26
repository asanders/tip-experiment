from alignment_data_classes import *
from scipy import ndimage
import matplotlib.pyplot as plt

def alignment_subplot_3d():
    return 0

def alignment_subplot():
    return 0

def add_subplot(X, Y, wave, name, fig, ax):
    wave = ndimage.gaussian_filter(wave, 0.7)
    Z = wave

    ax.set_xlim(X.min(), X.max())
    ax.set_ylim(Y.min(), Y.max())

    c_levels = np.linspace(Z.min(), 1.05*Z.max(), 50)
    l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
    cmap = cm.Spectral_r
    norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
    lw = 0.5
    cfax = ax.contourf(X, Y, Z, c_levels,
                       norm=norm,
                       alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
    cax = ax.contour(X, Y, Z, l_levels,
                      #norm=norm,
                      linewidths=lw, colors='k', linestyles='solid')
    ax.text(0.05, 0.95, name, ha='left', va='top', color='white',
            fontsize=12, fontweight='bold', transform=ax.transAxes)
    return 0

def plot_afm_data(location):
    # get data #
    return 0

class alignment_plot:
    def __init__(self, location):
        self.location = location
        # initialise figure #    
        self.fig = plt.figure()
        update_figure()
        set_formatter()
        # create parameters subplot #
        params = load_parameters(location)
        # get data #
        # setup subplots #
    
    def update_figure(self):
        fig_width_cm = 35.0
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
    def __init__(self, fig, location):
        self.fig = fig
        self.location = location
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
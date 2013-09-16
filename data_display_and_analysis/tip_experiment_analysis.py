from library.data_classes.tip_experiment_data_classes import *
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# sort data
class sort_data:
    def __init__(self, data, data_sort):
        self.sorted_indices = np.argsort(data_sort)
        self.spectra_long = data.spectra_long[self.sorted_indices]
        if data.dual_pol: self.spectra_trans = data.spectra_trans[self.sorted_indices]
        self.step = data.step[self.sorted_indices]
        self.displacement = data.displacement[self.sorted_indices]
        self.current = data.current[self.sorted_indices]
        self.conductance = data.conductance[self.sorted_indices]
        self.force_y = data.force_y[self.sorted_indices]
        self.force_x = data.force_x[self.sorted_indices]
        
# bin and average sorted data
class bin_data:
    def __init__(self, data, bin_param, bins):
        # set up bins and binning #
        self.bins = bins
        self.n_bins = len(bins)-1
        self.digitized = np.digitize(bin_param, self.bins)
        self.binned_param = np.array([bin_param[self.digitized==i].mean() for i in range(1, len(self.bins))])
        self.bin_axis = np.array([(self.bins[i]+self.bins[i-1])/2 for i in range(1, len(self.bins))])
        # bin data #
        self.step = np.array([data.step[self.digitized==i].mean() for i in range(1, len(self.bins))])
        self.displacement = np.array([data.displacement[self.digitized==i].mean() for i in range(1, len(self.bins))])
        self.current = np.array([data.current[self.digitized==i].mean() for i in range(1, len(self.bins))])
        self.conductance = np.array([data.conductance[self.digitized==i].mean() for i in range(1, len(self.bins))])
        self.force_y = np.array([data.force_y[self.digitized==i].mean() for i in range(1, len(self.bins))])
        self.force_x = np.array([data.force_x[self.digitized==i].mean() for i in range(1, len(self.bins))])
        # spectra data more complicated to bin #
        binned_spectra = np.array([data.spectra_long[self.digitized==i] for i in range(1, len(self.bins))])
        average_spectra = np.empty((len(self.bins)-1, len(data.wavelength_long)))
        for i in range(1, len(self.bins)):
            s_bin = binned_spectra[i-1]
            n_spectra, n_points = s_bin.shape
            temp_spectra = np.zeros(n_points)
            for spectra in s_bin: temp_spectra += spectra
            temp_spectra /= n_spectra
            average_spectra[i-1, :] = temp_spectra[:]
        self.spectra_long = average_spectra
        if data.dual_pol:
            binned_spectra = np.array([data.spectra_trans[self.digitized==i] for i in range(1, len(self.bins))])
            for i in range(1, len(self.bins)):
                s_bin = binned_spectra[i-1]
                n_spectra, n_points = s_bin.shape
                temp_spectra = np.zeros(n_points)
                for spectra in s_bin: temp_spectra += spectra
                temp_spectra /= n_spectra
                binned_spectra[i-1] = temp_spectra
            self.spectra_trans = binned_spectra
        # axis data #
        self.wavelength_long = data.wavelength_long
        if data.dual_pol: self.wavelength_trans = data.wavelength_trans
        # clean up missing values #
        self.binned_param = np.nan_to_num(self.binned_param)
        self.binned_param = np.ma.masked_equal(self.binned_param, 0.0)
        self.bin_axis = self.bin_axis[self.binned_param.mask == False]
        self.step = self.step[self.binned_param.mask == False]
        self.displacement = self.displacement[self.binned_param.mask == False]
        self.current = self.current[self.binned_param.mask == False]
        self.conductance = self.conductance[self.binned_param.mask == False]
        self.force_y = self.force_y[self.binned_param.mask == False]
        self.force_x = self.force_x[self.binned_param.mask == False]
        self.spectra_long = self.spectra_long[self.binned_param.mask == False]
        if data.dual_pol: self.spectra_trans = self.spectra_trans[self.binned_param.mask == False]
        
        
        

def display_data(data, x_ax_data, y_ax_data):
    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    Z = np.nan_to_num(data)
    Xi = x_ax_data
    Yi = np.nan_to_num(y_ax_data)
    minimum = Z.min()
    maximum = Z.max()
    # set colour mapping for all axes #
    c_levels = np.linspace(minimum, 1.05*maximum, 100)
    # create longitudinal spectral image subplot #
    X, Y = np.meshgrid(Xi, Yi)
    cfax = ax.contourf(X, Y, Z, c_levels,
                        alpha=1.0, cmap=cm.get_cmap(cm.Spectral_r, len(c_levels)-1))
    # add colour bar to far right of figure #
    cb = plt.colorbar(cfax, shrink=0.75, extend='both')
    cb.set_label('optical scattering (a.u.)')
    #ax.set_yscale('log')
    ax.xaxis.set_major_formatter(formatter)

if __name__ == '__main__':
    # correct data #
    data = spatial_data('c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data/nov_2012/day_21_tip_exp_1')
    data.spectra_long = data.spectra_long.T
    data.spectra_long = data.spectra_long[1:]
    data.step = np.linspace(0, data.spectra_long.shape[0], data.spectra_long.shape[0])
    data.rescale_wavelength()
    data.set_wavelength_roi(500e-9, 900e-9)
    data.set_step_roi(100, data.step[-1])
    display_data(data.spectra_long, data.wavelength_long, data.step)
    fig_folder = 'c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data'
    fname = os.path.join(fig_folder, 'raw_data')
    plt.savefig(fname + '.png', bbox_inches=0)
    #
    sorted_data = sort_data(data, data.conductance)
    display_data(sorted_data.spectra_long, data.wavelength_long, sorted_data.conductance)
    fig_folder = 'c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data'
    fname = os.path.join(fig_folder, 'sorted_conductance')
    plt.savefig(fname + '.png', bbox_inches=0)
    #
    for n_bins in [10,20,30,40,50,100]:
        bins = np.logspace(np.log10(data.conductance.min()), np.log10(data.conductance.max()), n_bins)
        bins[0] = 0.0
        binned_data = bin_data(data, data.conductance, bins)
        display_data(binned_data.spectra_long, data.wavelength_long, binned_data.bin_axis)
        fig_folder = 'c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data'
        fname = os.path.join(fig_folder, 'binned_conductance_bins_' + str(binned_data.n_bins))
        plt.savefig(fname + '.png', bbox_inches=0)
        display_data(binned_data.spectra_long, data.wavelength_long, binned_data.conductance)
        fig_folder = 'c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data'
        fname = os.path.join(fig_folder, 'binned_conductance_' + str(binned_data.n_bins))
        plt.savefig(fname + '.png', bbox_inches=0)
    #
    plt.show()
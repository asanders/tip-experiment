import sys
sys.path.append('C:\\Users\\Alan\\Documents\\PhD\\GitHub\\spectra-fit\\spectra_fit')
import spectra_fit
import numpy as np
from library.data_classes.tip_experiment_data_classes import *
from tip_experiment_analysis import *

import os
from igor.binarywave import load as loadibw
import matplotlib.pyplot as plt
from matplotlib import cm

class fit_spectral_image:
    def __init__(self, spectral_image, axis, model_crit):
        self.spectral_image = spectral_image
        self.axis = axis
        self.model_crit = model_crit
        
        def fit_spectra(self):
            for spectrum in self.spectral_image:
                # load corresponding model
                #fit = fit_spectra(noisy_spectra, wavelength, model_modes)
                pass

def fit_specim(specim, wav, model_crit):
    fitim = np.zeros_like(specim)
    peaks = np.zeros((specim.shape[0],2))
    num_spec = specim.shape[0]
    for i in range(num_spec):
        spec = specim[i]
        model = model_crit(i)
        fit = spectra_fit.fit_spectra(spec, wav, model)
        fitim[i] = fit.fitted_spectra
        peaks[i] = np.array([fit.parameters['dipole_centre'].value, fit.parameters['quad_centre'].value])
    return fitim, peaks

def display_data(data, x_ax_data=None, y_ax_data=None):
    if x_ax_data == None: x_ax_data = np.linspace(0, data.shape[1], data.shape[1])
    if y_ax_data == None: y_ax_data = np.linspace(0, data.shape[0], data.shape[0])
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
    ax.set_yscale('log')
    ax.xaxis.set_major_formatter(formatter)                
                                                
if __name__ == '__main__':
    data_loc = 'c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data/nov_2012/day_21_tip_exp_1'
    data = spatial_data(data_loc)
    data.spectra_long = data.spectra_long.T
    data.spectra_long = data.spectra_long[1:]
    data.step = np.linspace(0, data.spectra_long.shape[0], data.spectra_long.shape[0])
    data.rescale_wavelength()
    data.set_wavelength_roi(500e-9, 820e-9)
    
    bins = np.logspace(np.log10(data.conductance.min()), np.log10(data.conductance.max()), 41)
    bins[0] = 0.0
    data = bin_data(data, data.conductance, bins)            
    
    display_data(data.spectra_long, data.wavelength_long, data.bin_axis)
    print 'image displayed'
    def get_model_file(i):
        model_loc = os.path.join(data_loc, 'analysis')
        if i < 4: #i < 110:
            model = spectra_fit.load_model(os.path.join(model_loc,'classical_regime.txt'))
        elif i>=4 and i<20: #i >=110 and i < 229:
            model = spectra_fit.load_model(os.path.join(model_loc,'tunnelling_regime.txt'))
        else:
            model = spectra_fit.load_model(os.path.join(model_loc,'conductive_regime.txt'))
        return model
    fitim, peaks = fit_specim(data.spectra_long, data.wavelength_long, get_model_file)
    print 'fitted'
    display_data(fitim, data.wavelength_long, data.bin_axis)
    plt.figure()
    plt.plot(data.bin_axis, peaks[:,0], 'ro-')
    plt.twinx()
    plt.plot(data.bin_axis, peaks[:,1], 'bo-')
    plt.show()
    print 'finished'
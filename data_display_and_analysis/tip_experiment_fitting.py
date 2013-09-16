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
        
        self.fits = []
        self.fit()
        
        self.fitted_spectra = np.zeros_like(self.spectral_image)
        for i in range(self.spectral_image.shape[0]):
            self.fitted_spectra[i] = self.fits[i].fitted_spectra
        
    def fit(self):
        save_dir = 'c:/users/alan/skydrive/documents/phd/0 - experiment/data/best data/nov_2012/day_21_analysis'
        num_spec = self.spectral_image.shape[0]
        for i in range(num_spec):
            model, model_name = self.model_crit(i)
            fit = spectra_fit.fit_spectra(self.spectral_image[i], self.axis, model)
            self.fits.append(fit)
            
            plt.figure()
            plt.plot(fit.axis, fit.spectra, 'k.')
            plt.plot(fit.axis, fit.fitted_spectra, 'r-')
            for mode in fit.fitted_modes:
                plt.plot(fit.axis, fit.fitted_modes[mode], 'r--')
            fname = os.path.join(save_dir, 'spec_'+str(i)+'_'+model_name)
            plt.savefig(fname + '.png', bbox_inches=0)
            plt.close()

def fit_specim(specim, wav, model_crit):
    fitim = np.zeros_like(specim)
    peaks = np.zeros((specim.shape[0],2))
    num_spec = specim.shape[0]
    for i in range(num_spec):
        spec = specim[i]
        model, model_name = model_crit(i)
        fit = spectra_fit.fit_spectra(spec, wav, model)
        fitim[i] = fit.fitted_spectra
        peaks[i] = np.array([fit.parameters['dipole_centre'].value, fit.parameters['quad_centre'].value])
    return fit, peaks

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
    data.set_wavelength_roi(510e-9, 830e-9)
    
    bins = np.logspace(np.log10(data.conductance.min()), np.log10(data.conductance.max()), 41)
    bins[0] = 0.0
    #data = bin_data(data, data.conductance, bins)            
    
    #display_data(data.spectra_long, data.wavelength_long, data.bin_axis)
    print 'image displayed'
    def get_model_file2(i):
        model_loc = os.path.join(data_loc, 'analysis')
        if i < 4: #i < 110:
            model_name = 'classical'
            model = spectra_fit.load_model(os.path.join(model_loc,'classical_regime.txt'))
        elif i>=4 and i<19: #i >=110 and i < 229:
            model_name = 'tunnelling'
            model = spectra_fit.load_model(os.path.join(model_loc,'tunnelling_regime.txt'))
        else:
            model_name = 'conductive'
            model = spectra_fit.load_model(os.path.join(model_loc,'conductive_regime.txt'))
        return model, model_name
    def get_model_file(i):
        model_loc = os.path.join(data_loc, 'analysis')
        if i < 110:
            model_name = 'classical'
            model = spectra_fit.load_model(os.path.join(model_loc,'classical_regime.txt'))
        elif i >=110 and i < 229:
            model_name = 'tunnelling'
            model = spectra_fit.load_model(os.path.join(model_loc,'tunnelling_regime.txt'))
        else:
            model_name = 'conductive'
            model = spectra_fit.load_model(os.path.join(model_loc,'conductive_regime.txt'))
        return model, model_name
    fit, peaks = fit_specim(data.spectra_long, data.wavelength_long, get_model_file)
    fit = fit_spectral_image(data.spectra_long, data.wavelength_long, get_model_file)
    
    #for i in range(fit.fitted_spectra.shape[0]):
    #    for mode in fit.fits[i].model.modes:
    #        print mode
    #        if 'bkgd' in mode: print mode
    print 'fitted'
    #display_data(fit.fitted_spectra, data.wavelength_long, data.bin_axis)
    
    mode_specs = np.zeros_like(fit.fitted_spectra)
    for i in range(fit.spectral_image.shape[0]):
            mode_specs[i] = fit.fits[i].fitted_modes['dipole'] + fit.fits[i].fitted_modes['quad']
    display_data(mode_specs, data.wavelength_long, data.step)
    
    #plt.figure()
    #plt.plot(data.bin_axis, peaks[:,0], 'ro-')
    #plt.twinx()
    #plt.plot(data.bin_axis, peaks[:,1], 'bo-')
    plt.show()
    print 'finished'
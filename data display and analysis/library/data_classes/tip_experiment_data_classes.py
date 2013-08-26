import os
from igor.binarywave import load as loadibw
import numpy as np
from scipy import ndimage

class spatial_data:
    def __init__(self, location):
        self.location = location
        # initialise experimental variables and data #
        self.spectra_long = loadibw(os.path.join(location, "spec2d.ibw"))['wave']['wData'].T
        self.wavelength_long = loadibw(os.path.join(location, "wavelength.ibw"))['wave']['wData']
        self.step = np.linspace(0, self.spectra_long.shape[0], self.spectra_long.shape[0])
        try:
            self.dual_pol = True
            self.spectra_trans = loadibw(os.path.join(location, "spec2d_t.ibw"))['wave']['wData'].T
            self.wavelength_trans = loadibw(os.path.join(location, "wavelength_t.ibw"))['wave']['wData']
        except:
            self.dual_pol = False
        self.displacement = loadibw(os.path.join(location, "displacement.ibw"))['wave']['wData']
        self.current = loadibw(os.path.join(location, "current.ibw"))['wave']['wData']
        self.conductance = loadibw(os.path.join(location, "conductance.ibw"))['wave']['wData']
        self.force_y = loadibw(os.path.join(location, "psd_y.ibw"))['wave']['wData']
        self.force_x = loadibw(os.path.join(location, "psd_x.ibw"))['wave']['wData']
        self.scan_n = int(os.path.basename(location).rsplit("_", 1)[1])
        
        # add analysis variables #
        self.analysed = 0
        self.stoc = 0
        self.energy_long = np.array([])
        if self.dual_pol: self.energy_trans = np.array([])
        # scale data if necessary #
        self.scale_data()
        # analyse data #
        self.analyse_data()
    
    def scale_data(self):
        self.displacement = 1000 * (self.displacement - self.displacement[0])
        self.get_energy()
        return 0
    
    def rescale_wavelength(self):
        self.wavelength_long = 1e-9 * self.wavelength_long
        if self.dual_pol:
            self.wavelength_trans = 1e-9 * self.wavelength_trans
        return 0
    
    def set_wavelength_roi(self, wavelength_min=400e-9, wavelength_max=1000e-9):
        '''Set the ROI of spectral image.'''
        wavelength_min_i = self.wavelength_to_index(self.wavelength_long, wavelength_min)
        wavelength_max_i = self.wavelength_to_index(self.wavelength_long, wavelength_max)
        self.wavelength_long = self.wavelength_long[wavelength_min_i:wavelength_max_i]
        self.spectra_long = self.spectra_long[:, wavelength_min_i:wavelength_max_i]
        if self.dual_pol:
            wavelength_min_i = self.wavelength_to_index(self.wavelength_trans, wavelength_min)
            wavelength_max_i = self.wavelength_to_index(self.wavelength_trans, wavelength_max)
            self.wavelength_trans = self.wavelength_trans[wavelength_min_i:wavelength_max_i]
            self.spectra_trans = self.spectra_trans[:, wavelength_min_i:wavelength_max_i]
        return 0
    
    def set_step_roi(self, step_min, step_max):
        self.step = self.step[step_min:step_max]
        self.spectra_long = self.spectra_long[step_min:step_max, :]
        if self.dual_pol: self.spectra_trans = self.spectra_trans[step_min:step_max, :]
        self.current = self.current[step_min:step_max]
        self.conductance = self.conductance[step_min:step_max]
        self.force_x = self.force_x[step_min:step_max]
        self.force_y = self.force_y[step_min:step_max]
        self.displacement = self.displacement[step_min:step_max]
    
    def wavelength_to_index(self, wavelength, wavelength_value):
        '''Returns the index closest to the requested wavelength value.'''
        i = 0
        while wavelength[i] <= wavelength_value:
            i += 1
            if i > len(wavelength): exit
        if abs(wavelength_value - wavelength[i]) <\
            abs(wavelength_value - wavelength[i-1]):
            return i
        else: return i-1
    
    def get_energy(self):
        '''Convert a wavelength list/array into an energy array (eV).'''
        c = 3e8; h = 6.626068e-34; e = 1.60217646e-19
        self.energy_long = (h/e) * np.array([c/wl for wl in self.wavelength_long], dtype = np.float)
        if self.dual_pol:
            self.energy_trans = (h/e) * np.array([c/wl for wl in self.wavelength_trans], dtype = np.float)
        return 0
    
    def smooth_spectra(self, factor=0.7):
        self.spectra_long = ndimage.gaussian_filter(self.spectra_long, factor)
        if self.dual_pol:
            self.sepctra_trans = ndimage.gaussian_filter(self.spectra_trans, factor)
    
    def analyse_data(self):
        self.find_stoc()
        self.analysed = 1
    
    def find_stoc(self):
        grad = np.gradient(self.force_y)
        self.stoc = np.argmax(grad)
        return 0
        
class temporal_data:
    def __init__(self, parent, instance):
        # initialise experimental variables and data #
        self.instance = instance
        self.parent = parent
        self.location = os.path.join(parent, "time_resolved_data")
        self.scan_n = os.path.basename(parent).rsplit("_", 1)[1]
        
        self.spectra_long = loadibw(os.path.join(self.location, "qc_spec_"+instance+".ibw"))['wave']['wData'].T
        self.wavelength_long = loadibw(os.path.join(self.location, "qc_spec_"+instance+"_wavelength.ibw"))['wave']['wData']
        self.spectra_time = loadibw(os.path.join(self.location, "qc_spec_"+instance+"_time.ibw"))['wave']['wData']
        self.spectra_time = self.spectra_time[:-6]
        self.current = loadibw(os.path.join(self.location, "qc_trace_"+instance+".ibw"))['wave']['wData']
        self.conductance = loadibw(os.path.join(self.location, "qcg_trace_"+instance+".ibw"))['wave']['wData']
        self.force_y = loadibw(os.path.join(self.location, "qc_force_"+instance+".ibw"))['wave']['wData']
        self.dso_time = np.linspace(0, 20e-3, len(self.conductance))
        
        # add analysis variables #
        self.energy_long = np.array([])
        # scale data if necessary #
        self.scale_data()
    
    def scale_data(self):
        self.wavelength_long = 1e-9 * self.wavelength_long
        self.get_energy()
        return 0
    
    def set_wavelength_roi(self, wavelength_min=400e-9, wavelength_max=1000e-9):
        '''Set the ROI of spectral image.'''
        wavelength_min_i = self.wavelength_to_index(self.wavelength_long, wavelength_min)
        wavelength_max_i = self.wavelength_to_index(self.wavelength_long, wavelength_max)
        self.wavelength_long = self.wavelength_long[wavelength_min_i:wavelength_max_i]
        self.spectra_long = self.spectra_long[wavelength_min_i:wavelength_max_i, :]
        return 0
    
    def set_step_roi(self, step_min, step_max):
        self.step = self.step[step_min:step_max]
        self.spectra_long = self.spectra_long[step_min:step_max, :]
        if self.dual_pol: self.spectra_trans = self.spectra_trans[step_min:step_max, :]
        self.current = self.current[step_min:step_max]
        self.conductance = self.conductance[step_min:step_max]
        self.force_x = self.force_x[step_min:step_max]
        self.force_y = self.force_y[step_min:step_max]
        self.displacement = self.displacement[step_min:step_max]
    
    def wavelength_to_index(self, wavelength, wavelength_value):
        '''Returns the index closest to the requested wavelength value.'''
        i = 0
        while wavelength[i] <= wavelength_value:
            i += 1
            if i > len(wavelength): exit
        if abs(wavelength_value - wavelength[i]) <\
            abs(wavelength_value - wavelength[i-1]):
            return i
        else: return i-1
    
    def get_energy(self):
        '''Convert a wavelength list/array into an energy array (eV).'''
        c = 3e8; h = 6.626068e-34; e = 1.60217646e-19
        self.energy_long = (h/e) * np.array([c/wl for wl in self.wavelength_long], dtype = np.float)
        return 0
        
    def smooth_spectra(self, factor=0.7):
        self.spectra_long = ndimage.gaussian_filter(self.spectra_long, factor)
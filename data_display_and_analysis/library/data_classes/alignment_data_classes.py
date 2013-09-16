from igor.binarywave import load as loadibw
import numpy as np
import os
import sys
sys.path.append('C:\\Users\\Alan\\Documents\\PhD\\GitHub\\tip-experiment\\data_display_and_analysis')
from library.methods.gaussian_fitting import *

def load_itx(fname, location):
    with open(os.path.join(location, fname)) as f:
        lines = f.readlines()
        import re
        lines = re.split('\t|\r|\n', lines[0])
        lines = [line.strip('\r') for line in lines if line != '']
        # get array dimensions #
        for line in lines:
            if '/N=' in line:
                dimsize = line.split('/N=')[1].strip('()').split(',')
                dimsize = [int(x) for x in dimsize]
                dimsize = tuple(dimsize)
        # find BEGIN #
        for line in lines:
            if 'BEGIN' in line:
                i_begin = lines.index(line)
                break
        # find END #
        for line in reversed(lines):
            if 'END' in line:
                i_end = lines.index(line)
                break
        # extract data #
        data = np.array(lines[i_begin+1:i_end], dtype=np.float64).reshape(dimsize)
        # extract x scaling #
        for line in reversed(lines):
            if 'SetScale/P x ' in line:
                x0, dx = line.split('SetScale/P x ')[1].split(',')[0:2]
                x0 = float(x0)
                dx = float(dx)
                x = np.zeros(dimsize[0])
                for i in range(0, len(x)):
                    x[i] = x0 + i*dx 
            if 'SetScale/P y ' in line:
                y0, dy = line.split('SetScale/P y ')[1].split(',')[0:2]
                y0 = float(y0)
                dy = float(dy)
                y = np.zeros(dimsize[1])
                for i in range(0, len(y)):
                    y[i] = y0 + i*dy
        #for line in lines: print line
    return data, x, y

def load_parameters(location):
    parameters = loadibw(os.path.join(location, 'parameters.ibw'))['wave']['wData']
    parameters = parameters.flatten()
    key, values = np.split(parameters, 2)
    params = {}
    for k, v in zip(key, values): params[k] = v
    return params

class afm_alignment_data:
    def __init__(self, location):
        self.location = location
        
        # get alignment data #
        try:
            self.amplitude, self.x, self.y = load_itx('alignment_scan_fr.itx', location)
            self.phase, self.x, self.y = load_itx('alignment_scan_ftheta.itx', location)
        except IOError:
            raise IOError
        
        #self.amplitude = loadibw(os.path.join(location, "alignment_scan_fr.ibw"))['wave']['wData'].T
        #self.phase = loadibw(os.path.join(location, "alignment_scan_ftheta.ibw"))['wave']['wData'].T
        #self.x = loadibw(os.path.join(location, "wavelength.ibw"))['wave']['wData']
        #self.y = 0
        
        # get alignment variables #
        params = load_parameters(self.location)
        self.params = params
        self.set = int(params['alignment_set'])
        self.voltage = float(params['voltage'])
        self.position = float(params['init_pos_a'])
        self.time = params['time_stamp']
        self.scan_n = int(os.path.basename(location).rsplit("_", 1)[1])
        self.scan_size = 1000*float(params['scan_size'])
        self.scan_step = 1000*float(params['scan_step'])
        
        # analysis variables #
        self.amplitude_x0 = 0
        self.amplitude_y0 = 0
        self.amplitude_x_fwhm = 0
        self.amplitude_y_fwhm = 0
        self.phase_x0 = 0
        self.phase_y0 = 0
        self.phase_x_fwhm = 0
        self.phase_y_fwhm = 0
        # analysis arrays #
        # from igor - w_coef[0] = {z0, a0, x0, sigx, y0, sigy, corr} #
        self.amplitude_params = loadibw(os.path.join(location, 'fr_w_coef.ibw'))['wave']['wData']
        self.amplitude_errors = loadibw(os.path.join(location, 'fr_w_sigma.ibw'))['wave']['wData']
        self.amplitude_params = np.array([self.amplitude_params[1],
                                        self.amplitude_params[2],
                                        self.amplitude_params[4],
                                        self.amplitude_params[3],
                                        self.amplitude_params[5]])
        self.amplitude_fit = gaussian(*self.amplitude_params)
        self.phase_params = loadibw(os.path.join(location, 'ftheta_w_coef.ibw'))['wave']['wData']
        self.phase_errors = loadibw(os.path.join(location, 'ftheta_w_sigma.ibw'))['wave']['wData']
        self.phase_params = np.array([self.phase_params[1],
                                    self.phase_params[2],
                                    self.phase_params[4],
                                    self.phase_params[3],
                                    self.phase_params[5]])
        self.phase_fit = gaussian(*self.phase_params)
        
    def fit_data(self):
        self.amplitude_params = fitgaussian(self.amplitude)
        self.amplitude_params[1] *= (self.x[1]-self.x[0])   # modify x scaling
        self.amplitude_params[3] *= (self.x[1]-self.x[0])   # modify x scaling
        self.amplitude_params[2] *= (self.y[1]-self.y[0])   # modify y scaling
        self.amplitude_params[4] *= (self.y[1]-self.y[0])   # modify y scaling
        self.amplitude_params[1] += self.x[0]
        self.amplitude_params[2] += self.y[0]
        self.amplitude_fit = gaussian(*self.amplitude_params)
        # manipulate phase to invert it #
        phase = -1 * self.phase
        offset = phase.min()
        phase -= offset
        self.phase_params = fitgaussian(phase)
        self.phase_params[0] += offset
        self.phase_params[0] *= -1
        self.phase_params[1] *= (self.x[1]-self.x[0])   # modify x scaling
        self.phase_params[3] *= (self.x[1]-self.x[0])   # modify x scaling
        self.phase_params[2] *= (self.y[1]-self.y[0])   # modify y scaling
        self.phase_params[4] *= (self.y[1]-self.y[0])   # modify y scaling
        self.phase_params[1] += self.x[0]
        self.phase_params[2] += self.y[0]
        self.phase_fit = gaussian(*self.phase_params)
        

class current_alignment_data:
    def __init__(self, location):
        self.location = location
        
class resonance_data:
    def __init__(self, location):
        self.location = location
        
if __name__ == '__main__':
    afm_data = afm_alignment_data("H:\\data\\raw data\\aug_2013\\day_02\\alignment_scans\\scan_40")
    #try:
    #    afm_data_2 = afm_alignment_data("nothing")
    #except IOError:
    #    print "no data"
    
    from pylab import *
    matshow(afm_data.amplitude, cmap=cm.Spectral_r)
    contour(afm_data.amplitude_fit(*indices(afm_data.amplitude.shape)), cmap=cm.copper)
    ax = gca()
    (height, x, y, width_x, width_y) = afm_data.amplitude_params
    text(0.95, 0.05, """
    x : %.1f
    y : %.1f
    width_x : %.1f
    width_y : %.1f""" %(x, y, width_x, width_y),
            fontsize=16, horizontalalignment='right',
            verticalalignment='bottom', transform=ax.transAxes)
    matshow(afm_data.phase, cmap=cm.Spectral_r)
    contour(afm_data.phase_fit(*indices(afm_data.phase.shape)), cmap=cm.copper)
    ax = gca()
    (height, x, y, width_x, width_y) = afm_data.phase_params
    text(0.95, 0.05, """
    x : %.1f
    y : %.1f
    width_x : %.1f
    width_y : %.1f""" %(x, y, width_x, width_y),
            fontsize=16, horizontalalignment='right',
            verticalalignment='bottom', transform=ax.transAxes)
    show()
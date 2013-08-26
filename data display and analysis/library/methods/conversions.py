import numpy as np

def wavelength_to_index(wavelength, wl_array):
    i = 0
    while wl_array[i] <= wavelength:
        i += 1
        if i > len(wl_array):
            exit
    if abs(wavelength - wl_array[i]) < abs(wavelength - wl_array[i-1]):
        return i
    else:
        return i-1

def make_frequency_array(wavelength):
    """
    Convert a wavelength list/array into a frequency array (Hz).
    """
    #wavelength *= 1e-9
    c = 3e8
    frequency = np.array([c/wl for wl in wavelength], dtype = np.float)
    return frequency

def make_energy_array(wavelength):
    """
    Convert a wavelength list/array into an energy array (eV).
    """
    #wavelength *= 1e-9
    c = 3e8; h = 6.626068e-34; e = 1.60217646e-19
    energy = (h/e) * np.array([c/wl for wl in wavelength], dtype = np.float)
    return energy

if __name__ == '__main__':
    wavelength = np.linspace(400, 1000, 10)
    print "wavelength =", wavelength
    energy = make_energy_array(wavelength)
    print "energy =", energy
    print "index =", wavelength_to_index(600e-9, wavelength)

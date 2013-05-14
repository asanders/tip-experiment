import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from conductor_creation import *

# define global parameters #
e = -1.6e-19
eps_0 = 8.85418782e-12
V_0 = 10.0
m = 3e-11
beta = 2.7e-8
k_0 = 0.2
f_s = 13.0e3 / 2
omega_s = 2*np.pi*f_s
omega_p = 2 * omega_s

def calculate_contribution(d_0, A_ov):
    k_e = k_0 - ((eps_0 * A_ov * V_0**2) / (2 * d_0**3))
    z_m1 = ((eps_0 * A_ov * V_0**2) /\
           (4 * d_0**2 * np.sqrt((k_e - m*omega_p**2)**2 + (beta * omega_p)**2)))
    phi_1 = (np.arctan((beta * omega_p) /\
                       (k_e - m * omega_p**2)))
    return z_m1, phi_1

def get_separation(surfaces, x, y):
    d_0s = np.array([])
    s1 = surfaces[0]
    s2 = surfaces[1]
    #print 'dx =', (s2[100][0] - s1[100][0]), 'dy =', (s2[100][1] - s1[100][1])
    #print s1.shape, s2.shape
    [s1.shape[0], s2.shape[0]]
    for i in range(min([s1.shape[0], s2.shape[0]])):
        x2 = x[s2[i][0]]
        x1 = x[s1[i][0]]
        y2 = y[s2[i][1]]
        y1 = y[s1[i][1]]
        d_0 = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        d_0s = np.append(d_0s, d_0)
    return d_0s

def main():
    # define typical starting configuration #
    d0 = 500e-9
    theta1 = np.radians(30)
    theta2 = np.radians(15)
    # typical 1 um grid scan with 50 nm resolution #
    x_offsets = np.arange(-2e-6, 2e-6, 50e-9)
    # initialise storage arrays for amplitude and phase #
    amplitude = np.array([])
    phase = np.array([])
    # scan tip 1 across tip 2 #
    k=0.0
    for x_offset in x_offsets:
        k+=1.0
        sys.stdout.write('\r'+str(100*k/len(x_offsets)))
        sys.stdout.flush()
        z_m1 = 0; phi_1 = 0
        # create tip config #
        x, y, space, charge_space, surfaces =\
           create_tip_space(d0, theta1, theta2, x_offset)

        # plot #
        X, Y = np.meshgrid(x, y)
        Z = charge_space.T
        c_levels = np.linspace(Z.min(), 1.05*Z.max(), 100)
        l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
        cmap = cm.Spectral_r
        norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
        lw = 0.5
        fig = plt.figure()
        ax = fig.add_subplot(111)
        cfax = ax.contourf(X, Y, Z, c_levels,
                            norm=norm,
                            alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
        cb = plt.colorbar(cfax)
        fname = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),\
                             'images\\'+str(x_offset))
        plt.savefig(fname + '.png', bbox_inches=0)
        plt.close()
        
        # determine separation between adjacent points on each tip #
        A_ov = ((x.max()-x.min())/len(x)) * ((y.max()-y.min())/len(y))
        d_0s = get_separation(surfaces, x, y)
        #print 'min $d_0$ =', d_0s.min()
        # for each separated point determine contribution to oscillation #
        for d_0 in d_0s:
            z_m1i, phi_1i = calculate_contribution(d_0, A_ov)
            z_m1 += z_m1i
            phi_1 += phi_1i
        # add total contibution to array #
        amplitude = np.append(amplitude, z_m1)
        phase = np.append(phase, phi_1)
    return amplitude, phase, x_offsets

if __name__ == '__main__':
    amplitude, phase, x_offsets = main()
    # plot #
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax2 = ax.twinx()
    ax.plot(x_offsets, amplitude, 'r-')
    ax2.plot(x_offsets, phase, 'b-')
    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter) 
    ax.yaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_formatter(formatter)
    plt.show()

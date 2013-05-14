import os
import numpy as np

def load_1d_data(target):
    with open(target, 'r') as f:
        data = f.read()
        data = data[data.find("BEGIN"):]
        data = data[:data.find("END")]
    data = (data.split("\r\t"))[1:]
    data = [float(x) for x in data]
    return np.array(data)

def load_2d_data(target):
    with open(target, 'r') as f:
        data = f.read()
        # get 2d dimensions
        ##l = (data.split("\t")[0]).find("/N=(")
        ##r = (data.split("\t")[0]).find(")")
        ##xy = (data.split("\t")[0][l+4:r]).split(",")
        ##xy = [int(i) for i in xy]
        # isolate data
        data = data[data.find("BEGIN"):]
        data = data[:data.find("END")]
    data = (data.split("\r\t"))[1:]
    data = [x.split("\t") for x in data]
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            data[i][j] = float(data[i][j])
    data = np.array(data)
    #data = np.flipud(data)
    return data

def load_2d_txt_data(target):
    with open(target, 'r') as f:
        data = f.read()
        # get 2d dimensions
        l = (data.split("\t")[0]).find("/N=(")
        r = (data.split("\t")[0]).find(")")
        xy = (data.split("\t")[0][l+4:r]).split(",")
        xy = [int(i) for i in xy]
        # isolate data
        data = data[data.find("BEGIN"):]
        data = data[:data.find("END")]
    data = (data.split("\r\t"))[1:]
    data = [x.split("\t") for x in data]
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            data[i][j] = str(data[i][j][1:-1])
    data = np.array(data)
    data = np.reshape(data, (xy[0], xy[1]))
    #data = np.flipud(data)
    return data

def load_params(target):
    params_wdata = load_2d_txt_data(os.path.join(target, "parameters.itx"))
    params = {}
    for x in params_wdata:
        # check values for NaNs #
        if x[1] == 'NaN':
            x[1] = raw_input("Error: " + x[0] + " = NaN. Replace with? ")
            print x[0], "set to", x[1]
        # format values from initial strings #
        if x[0] == 'time_stamp':
            params[x[0]] = x[1]
        elif (x[0] == 'alignment_set' or
              x[0] == 'electronic_alignment' or
              x[0] == 'force_alignment'):
            params[x[0]] = int(x[1])
        else:
            params[x[0]] = float(x[1])
        # fix any potentially missing entries #
    return params

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import scipy.ndimage as ndimage
    target = "C:\\Users\\Alan\\SkyDrive\\Documents\\Projects\\spectra2D.txt"
    wl_l = 260; wl_u = 790
    z = load_2d_data(target)
    z = z[1:, wl_l:wl_u]
    z2 = ndimage.gaussian_filter(z, sigma=1.0, order=0)
    z2 = np.flipud(z2)
    target = "C:\\Users\\Alan\\SkyDrive\\Documents\\Projects\\wavelengthImageAxis.txt"
    x = load_1d_data(target)
    x = x[wl_l:wl_u]
    target = "C:\\Users\\Alan\\SkyDrive\\Documents\\Projects\\PZdisplacement.txt"
    y = load_1d_data(target)
    y *= 1000
    y -= y[-1]
    #print "len(x) =", len(x), ", len(y) =", len(y), "shape(z) =", z2.shape

    X, Y = np.linspace(x.min(), x.max(), len(x)), np.linspace(y.min(), y.max(), len(y))
    X, Y = np.meshgrid(x, y)
    Z = z2.reshape(X.shape)
    
    #import scipy.interpolate
    #rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
    #z = rbf(X, Y)

    #dpi = 100
    #px,py = z2.shape
    #size = (py/np.float(dpi), px/np.float(dpi))

    fig = plt.figure()#(figsize=size, dpi=dpi)
    ax = fig.add_subplot(121)
    cax = ax.imshow(z, vmin=z.min(), vmax=z.max(),
                    origin='lower', aspect='auto',
                    extent=[x.min(), x.max(), y.min(), y.max()])
    fig.colorbar(cax)
    ax = fig.add_subplot(122)
    ax.contourf(X, Y, Z, 8, alpha=0.75)
    ax.contour(X, Y, Z, 8, linewidth=.5)
    plt.xlabel('wavelength (nm)')
    plt.ylabel('PZ position (nm)')
    plt.show()
    
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X, Y = np.meshgrid(x, y)
    Z = z2.reshape(X.shape)
    ax.plot_surface(X, Y, Z, cmap='jet')
    ax.set_xlabel('wavelength (nm)')
    ax.set_ylabel('PZ displacement (nm)')
    ax.set_zlabel('optical scattering (a.u.)')
    plt.show()

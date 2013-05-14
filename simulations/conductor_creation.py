import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc

# 2d shapes #

def create_tips(d0, theta1, theta2, x_offset):
    def create_tip1(x,y):
        # left (x < 0) tip surface defined by equation  #
        # y - (1.0/np.tan(theta1))*x + d0/2 = 0         #
        if (y - (1.0/np.tan(theta1))*(x-x_offset) + d0/2) <= 0 and (x-x_offset) < 0:
            return 1
        # right (x >= 0) tip surface defined by equation  #
        # y + (1.0/np.tan(theta2))*x + d0/2 = 0           #
        elif y + (1.0/np.tan(theta2))*(x-x_offset) + d0/2 <= 0 and (x-x_offset) >= 0:
            return 1
        else:
            return 0
    def create_tip2(x,y):
        # left (x < 0) tip surface defined by equation  #
        # y + (1.0/np.tan(theta2))*x - d0/2 = 0         #
        if y + (1.0/np.tan(theta2))*x - d0/2 >= 0 and x < 0:
            return 1
        # right (x >= 0) tip surface defined by equation  #
        # y - (1.0/np.tan(theta1))*x - d0/2 = 0           #
        elif y - (1.0/np.tan(theta1))*x - d0/2 >= 0 and x >= 0:
            return 1
        else:
            return 0
    return create_tip1, create_tip2

def create_plates(d0):
    def create_plate1(x,y):
        # plate surface defined by equation y + d0/2 = 0 #
        if y + d0/2 <= 0:
            return 1
        else:
            return 0
    def create_plate2(x,y):
        # plate surface defined by equation y - d0/2 = 0 #
        if y - d0/2 <= 0:
            return 1
        else:
            return 0
    return create_plate1, create_plate2

def add_object(object_func, x, y, space):
    new_space = np.array(space)
    # add objects to space #
    for i in range(len(x)):
        for j in range(len(y)):
            new_space[i][j] += object_func(x[i], y[j])
    return new_space

def charge_distribution(object_name, x, y, space):
    # find surfaces storing charge #
    charge_space = np.zeros_like(space)
    surface = np.array([]).reshape(0,3)
    if object_name == "tip1":
        q = 1.0
    else:
        q = -1.0
    for i in range(len(x)):
        for j in range(len(y)):
            il = i-1 if (i-1 >= 0) else 0
            iu = i+1 if (i+1 < len(x)) else i
            jl = j-1 if (j-1 >= 0) else 0
            ju = j+1 if (j+1 < len(y)) else j
            sur_space = space[il:iu+1,jl:ju+1]
            if space[i][j] == 1 and 1 in sur_space and 0 in sur_space:
                charge_space[i][j] = q
                row = np.array([i, j, q]).reshape(1,3)
                surface = np.append(surface, row, axis=0)               
    return charge_space, surface

def create_tip_space(d0, theta1, theta2, x_offset):
    # create grid space and dimension scaling #
    nx = 200; ny = 200; nz = 11
    x = np.linspace(-5e-6, 5e-6, nx)
    y = np.linspace(-5e-6, 5e-6, ny)
    z = np.linspace(-10e-6, 10e-6, nz)
    space = np.zeros((nx,ny))    # 2d space used for quick planar sims #

    # create objects #
    create_tip1, create_tip2 = create_tips(d0, theta1, theta2, x_offset)
    surfaces = np.array([])
    surface = np.array([])
    
    # add objects to space #
    charge_space = np.zeros_like(space)
    surfaces = []
    # tip 1
    t1_space = add_object(create_tip1, x, y, space)
    charge_space_1, charge_surface = charge_distribution('tip1', x, y, t1_space)
    charge_space += charge_space_1
    surfaces.append(charge_surface)
    t2_space = add_object(create_tip2, x, y, space)
    charge_space_2, charge_surface = charge_distribution('tip2', x, y, t2_space)
    charge_space += charge_space_2
    surfaces.append(charge_surface)
    space += t1_space
    space += t2_space
    return x, y, space, charge_space, surfaces

if __name__ == '__main__':
    # define object parameters #
    d0 = 2.0
    x_offset = 1.0
    theta1 = np.radians(30)
    theta2 = np.radians(15)
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
    #im = ax.imshow(Z)
    plt.show()

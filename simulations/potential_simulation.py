from conductor_creation import *

eps_0 = 8.85418782e-12

def calculate_potential(space, x, y, surfaces):
    potential = lambda q, r: q/(4*np.pi*eps_0*r)
    potential_space = np.zeros_like(space)
    for i in range(space.shape[0]):
        for j in range(space.shape[1]):
            if space[i][j] == 1 or space[i][j] == 2:
                continue
            else:
                for surface in surfaces:
                    for point in surface:
                        dx = x[i] - x[point[0]]
                        dy = y[j] - y[point[1]]
                        r = np.sqrt(dx**2 + dy**2)
                        #if r == 0: print "i=%d,\tj=%d,\tsx=%d,\tsy=%d,"\
                        #            "\tx=%.3f,\ty=%.3f,\tsx=%.3f,\tsy=%.3f"\
                        #   %(i, j, sx[k], sy[k], x[i], x[j], x[sx[k]], y[sy[k]])
                        potential_space[i][j] += potential(point[2], r)
    return potential_space

def calculate_field(space, x, y, surfaces):
    field = lambda q, dx, dy: np.array([dx,dy]) * q/(4*np.pi*eps_0*(np.sqrt(dx**2+dy**2))**3)
    field_space = np.zeros_like(space)
    for i in range(space.shape[0]):
        for j in range(space.shape[1]):
            if space[i][j] == 1 or space[i][j] == 2:
                continue
            else:
                for surface in surfaces:
                    for point in surface:
                        dx = x[i] - x[point[0]]
                        dy = y[j] - y[point[1]]
                        Ex, Ey = field(point[2], dx, dy)
                        field_space[i][j] += np.sqrt(Ex**2 + Ey**2)
    return field_space

#def calculate_field(potential_space):
#    field_space = np.zeros_like(potential_space)
#    Ex, Ey = np.gradient(potential_space)
#    for i in range(potential_space.shape[0]):
#        for j in range(potential_space.shape[1]):
#            field_space[i][j] = np.sqrt(Ex[i][j]**2 + Ey[i][j]**2)
#    return field_space

if __name__ == '__main__':
    d0 = 1e-6
    x_offset = 0.0
    theta1 = np.radians(30)
    theta2 = np.radians(15)
    x, y, space, charge_space, surfaces =\
       create_tip_space(d0, theta1, theta2, x_offset)
    print "created space"
    #potential_space = calculate_potential(space, x, y, surfaces)
    #print "calculated potential"
    field_space = calculate_field(space, x, y, surfaces)
    print "calculated field"

    # plot #
    X, Y = np.meshgrid(x, y)
    Z = field_space.T
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
    formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
    formatter.set_scientific(True) 
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter) 
    ax.yaxis.set_major_formatter(formatter)
    plt.show()

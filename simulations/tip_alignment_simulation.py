# modules #
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import rc

# MAIN PROGRAM #

# create grid space and dimension scaling #
nx = 20; ny = 20; nz = 100
#space = np.zeros((nx,ny,nz))
x = np.linspace(-10, 10, nx)
y = np.linspace(-5, 5, ny)
z = np.linspace(-5, 5, nz)
space_2d = np.zeros((nx,ny))            # 2d space used for quick planar sims

# define objects #
d0 = 2.0
theta1 = np.radians(20)
theta2 = theta1#np.radians(10)

# define alignment parameters #
V0 = 10

## define tips as being a 2d triangle for now ##
def create_tips(d0, theta1, theta2):
    # tip 1 boundary #
    t1b1 = lambda x,y: x - (1.0/np.tan(theta1))*y + d0/2
    t1b2 = lambda x,y: x + (1.0/np.tan(theta2))*y + d0/2
    # tip 2 boundary #
    t2b1 = lambda x,y: x + (1.0/np.tan(theta2))*y - d0/2
    t2b2 = lambda x,y: x - (1.0/np.tan(theta1))*y - d0/2
    return t1b1, t1b2, t2b1, t2b2

## define tips as being a 2d triangle for now ##
def create_plates(d0):
    # tip 1 boundary #
    t1b1 = lambda x,y: x + 5 + d0/2
    t1b2 = lambda x,y: x + 5 + d0/2
    # tip 2 boundary #
    t2b1 = lambda x,y: x - 5 - d0/2
    t2b2 = lambda x,y: x - 5 - d0/2
    return t1b1, t1b2, t2b1, t2b2

# add objects to space #
#t1b1, t1b2, t2b1, t2b2 = create_tips(d0, theta1, theta2)
t1b1, t1b2, t2b1, t2b2 = create_plates(d0)

# get tip surface coordinates #
s1x = np.array([])
s1y = np.array([])
s2x = np.array([])
s2y = np.array([])
for i in range(len(x)):
    for j in range(len(y)):
        # tip 1 #
        if (abs(t1b1(x[i],y[j])) <= 0.1 and t1b2(x[i],y[j]) <= 0)\
           or (abs(t1b2(x[i],y[j])) <= 0.1 and t1b1(x[i],y[j]) <= 0):
            s1x = np.append(s1x, x[i])
            s1y = np.append(s1y, y[j])
        # tip 2 #
        elif (abs(t2b1(x[i],y[j])) <= 0.1 and t2b2(x[i],y[j]) >= 0)\
             or (abs(t2b2(x[i],y[j])) <= 0.1 and t2b1(x[i],y[j]) >= 0):
            s2x = np.append(s2x, x[i])
            s2y = np.append(s2y, y[j])
#print s1x
#print s1y
#print s2x
#print s2y

e0 = 8.85418782e-12
potential= lambda q, r: q/(4*np.pi*e0*r)

# calculate system potential #
k=0.0
for i in range(len(x)):
    for j in range(len(y)):
        k+=1
        sys.stdout.write('\r'+str(100*k/(len(x)*len(y))))
        sys.stdout.flush()
        # V = V0 inside conductors #
        ## tip 1 ##
        if t1b1(x[i],y[j]) <= 0 and t1b2(x[i],y[j]) <= 0:
            space_2d[i][j] = V0
        ## tip 2 ##
        elif t2b1(x[i],y[j]) >= 0 and t2b2(x[i],y[j]) >= 0:
            space_2d[i][j] = -V0
        # calculate potential outside conductors #
        else:
            V = 0
            # loop over tip surfaces #
            for ii in range(len(s1x)):
                dx = x[i] - s1x[ii]
                dy = y[j] - s1y[ii]
                dr = np.sqrt(dx**2 + dy**2)
                if dr == 0:
                    continue
                else:
                    V += potential(1.0, dr)
            for jj in range(len(s2x)):
                dx = x[i] - s2x[jj]
                dy = y[j] - s2y[jj]
                dr = np.sqrt(dx**2 + dy**2)
                if dr == 0:
                    continue
                else:
                    V += potential(-1.0, dr)
            space_2d[i][j] = V
Ex, Ey = np.gradient(space_2d)
field_2d = np.sqrt(Ex**2 + Ey**2)

#print space_2d

# plot #
#print x.shape, y.shape, z.shape
X, Y = np.meshgrid(x, y)
Z = space_2d.T
#print X.shape, Y.shape, Z.shape
c_levels = np.linspace(Z.min(), 1.05*Z.max(), 100)
l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
cmap = cm.Spectral_r
norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
lw = 0.5

fig = plt.figure(figsize=(15, 5))
ax = fig.add_subplot(131)
#ax.plot(s1x, s1y, 'r.')
#ax.plot(s2x, s2y, 'b.')
cfax = ax.contourf(X, Y, Z, c_levels,
                    norm=norm,
                    alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
cb = plt.colorbar(cfax, shrink=1.0, extend='both')

Z = field_2d.T
c_levels = np.linspace(Z.min(), 1.05*Z.max(), 100)
l_levels = np.linspace(Z.min(), 1.05*Z.max(), 10)
cmap = cm.Spectral_r
norm = cm.colors.Normalize(vmax=Z.max(), vmin=Z.min())
ax = fig.add_subplot(132)
cfax = ax.contourf(X, Y, Z, c_levels,
                    norm=norm,
                    alpha=1.0, cmap=cm.get_cmap(cmap, len(c_levels)-1))
cb = plt.colorbar(cfax, shrink=1.0, extend='both')

ax = fig.add_subplot(133)
ax.quiver(X, Y, Ex, Ey)
plt.tight_layout()
plt.savefig('C:\\users\\alan\\desktop\\tips.png', bbox_inches=0)
plt.show()

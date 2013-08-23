import numpy as np

# Create empty charge spaces #

def create_space(x1, x2, y1, y2, dx, dy):
    '''
    Create a space with size (x2-x1,y2-y1) and grid spacings (dx,dy).
    '''
    n = (x2 - x1)/dx
    m = (y2 - y1)/dy
    space = create_space_step(x1,x2,y1,y2,n,m):
    return space

def create_space_step(x1, x2, y1, y2, n, m):
    '''
    Create a space with size (x2-x1,y2-y1) and (n,m) grid entries.
    '''
    x = np.linspace(x1,x2,n)
    y = np.linspace(y1,y2,m)
    space = create_space_nm(n,m)
    return space

def create_space_nm(n, m):
    '''
    Create an nxm grid space
    '''
    space = np.zeros((n,m), dtype=np.float64)
    return space

# Add objects to charge spaces #

def add_object(object_func, space):
    '''
    Add the object described by object_func to the given space.
    '''
    new_space = np.array(space)
    # add objects to space #
    for i in range(len(x)):
        for j in range(len(y)):
            new_space[i][j] += object_func(x[i], y[j])
    return new_space

## Objects (charge) functions ##

def add_point_charge(q, xi, yi, x, y, space):
    '''
    Add a point charge q at position (xi,yi) to the given space.
    '''
    ### error handling - point charge must be within grid space ###
    if xi > x.max() or xi < x.min() or\
       yi > y.max() or yi < y.min():
        return -1
    ### get grid index to place charge ###
    new_space = np.array(space)
    x_index = np.where(x==xi)
    y_index = np.where(y==yi)
    if x_index == []:
        delta = [abs(i - xi) for i in x]
        x_index = np.where(x==x.min())
    elif y_index = []
        delta = [abs(i - yi) for i in y]
        y_index = np.where(y==y.min())
    ### add charge to space ###
    new_space[x_index,y_index] = q
    return new_space

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
            return -1
        # right (x >= 0) tip surface defined by equation  #
        # y - (1.0/np.tan(theta1))*x - d0/2 = 0           #
        elif y - (1.0/np.tan(theta1))*x - d0/2 >= 0 and x >= 0:
            return -1
        else:
            return 0
    return create_tip1, create_tip2

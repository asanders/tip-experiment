import datetime
import os
import numpy as np
import matplotlib.pyplot as plt

def check_folder(d):
    """
    Checks the existence of a folder and creates a directory if nonexistent.
    """
    if not os.path.exists(d):
        os.makedirs(d)
    return d

def check_filefolder(f):
    """
    Checks the existence of a folder, given a filename,
    and creates a directory if nonexistent.
    """
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
    return d

def create_data_folder(root):
    """
    Creates a date-organised data folder structure in root to store data.
    Returns the full root + data location pathname as a string.
    """
    date = datetime.datetime.today()
    year = date.strftime("%Y")
    month = date.strftime("%b")#date.strftime("%m - %b")
    day = date.strftime("%d")
    f = root + "\\"; check_folder(f)
    f += month + " " + year + "\\"; check_folder(f)
    #f += month + "\\"; check_folder(f)
    f += "day " + day + "\\"; check_folder(f)
    return f

def save_fig(fig, name, current_folder):
    '''
    Save a figure of data in an experiment folder to the experiment day folder.
    Fig is the figure object,
    name is the string name of the figure within the day folder,
    and current_folder is the current folder from where the data was loaded.
    '''
    # identify day folder #
    fig_folder = os.path.dirname(current_folder)
    while "day" not in os.path.basename(fig_folder):
        fig_folder = os.path.dirname(fig_folder)
    # save figure to day folder #
    fname = os.path.join(fig_folder, name)
    print "saving figure to", fname, ".png"
    plt.savefig(fname + '.png', bbox_inches=0)

def save_data_array(data, fname):
    """
    Save an array to a file. Possible implementation methods are np.savetxt/np.genfromtxt or np.save/np.load.
    """
    fformat = ".dat"
    f = fname + fformat
    np.savetxt(f, data)
    fformat = ".npy"
    f = fname + fformat
    np.save(f, data)

def load_data_array(fname):
    """
    Load an array from a file. Possible implementation methods are np.savetxt/np.genfromtxt or np.save/np.load.
    """
    data = np.genfromtxt(fname)
    #data = np.load(fname)
    return data

if __name__ == "__main__":
    date = datetime.datetime.today()
    print date.strftime("%Y/%m/%d")
    root = "C:\\Users\\Alan\\SkyDrive\\Documents\\code\\python"
    create_data_folder(root)
    
    

import matplotlib.pyplot as plt
import numpy as np

class publication_figure:
    def __init__(self, fig_width_pt=246.0, aspect=None, span_columns=False):
        self.fig_width_pt = fig_width_pt
        self.aspect = aspect
        self.span = span_columns
        if self.span: self.fig_width_pt *= 2
        self.update_figure()
        self.formatter = self.set_formatter()
        self.fig = plt.figure()
        
    def update_figure(self):
        fig_width_pt = self.fig_width_pt
        inches_per_pt = 1.0/72.27
        fig_width = fig_width_pt * inches_per_pt
        if self.aspect is None: self.aspect = (np.sqrt(5)-1.0)/2.0
        fig_height = self.aspect * fig_width
        fig_size = (fig_width, fig_height)
        fig_params = {'backend': 'pdf',
                'font.size': 10,
                'axes.labelsize': 10,
                'text.fontsize': 10,
                'legend.fontsize': 8,
                'xtick.labelsize': 8,
                'ytick.labelsize': 8,
                'text.usetex': True,
                'font.family': 'serif',
                'axes.linewidth': 0.7,
                'patch.linewidth': 0.7,
                'figure.figsize': fig_size}
        plt.rcParams.update(fig_params)
    
    def set_formatter(self):
        formatter = plt.ScalarFormatter(useOffset=False, useMathText=True)
        formatter.set_scientific(True) 
        formatter.set_powerlimits((-3,3))
        return formatter
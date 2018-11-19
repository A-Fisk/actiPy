import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Script for defining decorators to be used for plotting functions
# all plotting functions need to take fig, ax as *args, and return
# fig and ax and params dict
def single_plot_kwarg_decorator(func):
    """
    Strictly decorating function intended to tidy up all the xlabels, ylabels
    , titles, and savefig/showfig functions
    :param func:
    :return:
    """
    def wrapper(data, *args, **kwargs):
        # this is only for a single plot so can set xlabel and ylabel
        # can call plots here

        # call the plotting function which will create the plots
        # and set the default values for all the labels
        fig, ax, params_dict = func(data)

        # set the extra values in kwargs
        fig.autofmt_xdate()
        xfmt = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(xfmt)
        
        interval = params_dict["interval"]
        if "interval" in kwargs:
            interval = kwargs["interval"]
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=interval))
        
        title = params_dict["title"]
        if "title" in kwargs:
            title = kwargs["title"]
        fig.suptitle(title)
        
        xlabel = params_dict["xlabel"]
        if "xlabel" in kwargs:
            xlabel = kwargs["xlabel"]
        ax.set_xlabel(xlabel)
        ylabel = params_dict["ylabel"]
        if "ylabel" in kwargs:
            ylabel = kwargs["ylabel"]
        ax.set_ylabel(ylabel)
        
        return fig, ax
    
    return wrapper

# Script for defining decorators to be used for plotting functions
# all plotting functions need to take fig, ax as *args, and return
# fig and ax and params dict
def multiple_plot_kwarg_decorator(func):
    """
    Strictly decorating function intended to tidy up all the xlabels, ylabels
    , titles, and savefig/showfig functions
    Uses fig instead of ax as multiple ax parameters
    :param func:
    :return:
    """
    def wrapper(data, *args, **kwargs):
        # this is only for a single plot so can set xlabel and ylabel
        # can call plots here

        # call the plotting function which will create the plots
        # and set the default values for all the labels
        fig, ax, params_dict = func(data, **kwargs)

        # set the x axis times to show only every few hours and look pretty
        fig.autofmt_xdate()
        xfmt = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(xfmt)
        interval = params_dict["interval"]
        if "interval" in kwargs:
            interval = kwargs["interval"]
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=interval))
        
        # set the legend to given location
        if "legend" in kwargs and kwargs["legend"]:
            location = 1
            if "legend_loc" in kwargs:
                location = kwargs["legend_loc"]
            # set the legend using only the final subplot values
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc=location)
        
        # set the xlimits of the plot to the given parameters
        if "xlim" in params_dict:
            xlim = params_dict["xlim"]
            if "xlim" in kwargs:
                xlim = kwargs["xlim"]
            ax.set(xlim=xlim)
        
        # set the plot title, the x axis label and the y axis label
        title = params_dict["title"]
        if "title" in kwargs:
            title = kwargs["title"]
        fig.suptitle(title)
        xlabel = params_dict["xlabel"]
        if "xlabel" in kwargs:
            xlabel = kwargs["xlabel"]
        ax.set_xlabel(xlabel)
        ylabel = params_dict["ylabel"]
        if "ylabel" in kwargs:
            ylabel = kwargs["ylabel"]
        fig.text(
            0.02,
            0.5,
            ylabel,
            ha="center",
            va='center',
            rotation='vertical'
        )
        
        return fig, ax
    
    return wrapper

def show_savefig_decorator(func):
    """
    Decotator for only creating the savefig, showfig and figsize kwarg
    arguments
    :param func:
    :return:
    """
    def wrapper(data, *args, **kwargs):
        
        fig, ax = func(data, *args, **kwargs)
        
        if "figsize" in kwargs:
            fig.set_size_inches(kwargs["figsize"])
        if "showfig" in kwargs and kwargs["showfig"]:
            plt.show()
        if "savefig" in kwargs and kwargs["savefig"]:
            plt.savefig(kwargs["fname"])
            plt.close()
            
    return wrapper


import pandas as pd
idx = pd.IndexSlice
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
    Timeaxis: Bool
    Interval: String for timeaxis
    legend: bool
    Legend_loc: string for location
    xlim: tuple
    title: string
    xlabel: string
    ylabel: string
    figsize: tuple
    showfig: bool
    savefig: bool
    :return:
    """
    def wrapper(data, *args, **kwargs):
        # this is only for a single plot so can set xlabel and ylabel
        # can call plots here

        # call the plotting function which will create the plots
        # and set the default values for all the labels
        fig, ax, params_dict = func(data, **kwargs)

        if "timeaxis" in params_dict and params_dict["timeaxis"]:
            # set the x axis times to show only every few hours and look pretty
            xfmt = mdates.DateFormatter("%H:%M")
            if "xfmt" in kwargs:
                xfmt = kwargs["xfmt"]
            ax.xaxis.set_major_formatter(xfmt)
            interval = params_dict["interval"]
            if "interval" in kwargs:
                interval = kwargs["interval"]
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=interval))
            fig.autofmt_xdate()
            
        # set the legend to given location
        if "legend" in kwargs and kwargs["legend"]:
            location = 1
            if "legend_loc" in kwargs:
                location = kwargs["legend_loc"]
            # set the legend using only the final subplot values
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc=location)
        
        # set the xlimits of the plot to the given parameters
        if "xlim" in params_dict or "xlim" in kwargs:
            if "xlim" in kwargs:
                xlim = kwargs["xlim"]
            else:
                xlim = params_dict["xlim"]
            ax.set(xlim=xlim)
        
        # set the plot title, the x axis label and the y axis label
        if "title" in params_dict or 'title' in kwargs:
            if "title" in params_dict:
                title = params_dict["title"]
            if "title" in kwargs:
                title = kwargs["title"]
            fig.suptitle(title)
        if params_dict["xlabel"] is not False:
            xlabel = params_dict["xlabel"]
            if "xlabel" in kwargs:
                xlabel = kwargs["xlabel"]
            if "xlabelpos" in kwargs:
                xlabelpos = kwargs["xlabelpos"]
            else:
                xlabelpos = (0.5, 0.05)
            fig.text(xlabelpos[0],
                     xlabelpos[1],
                     xlabel,
                     ha='center',
                     va='center')
        if params_dict["ylabel"] is not False:
            if "ylabel" in params_dict:
                ylabel = params_dict["ylabel"]
            if "ylabel" in kwargs:
                ax.set_ylabel("")
                ylabel = kwargs["ylabel"]
            if "ylabelpos" in kwargs:
                ylabelpos = kwargs["ylabelpos"]
            else:
                ylabelpos = (0.02, 0.5)
            fig.text(
                ylabelpos[0],
                ylabelpos[1],
                ylabel,
                ha="center",
                va='center',
                rotation='vertical'
            )
     
        if "figsize" in kwargs:
            fig.set_size_inches(kwargs["figsize"])
        if "showfig" in kwargs and kwargs["showfig"]:
            plt.show()
        if "savefig" in kwargs and kwargs["savefig"]:
            plt.savefig(kwargs["fname"])
            plt.close()
            
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


def set_title_decorator(func):
    """
    Decorator to set the "title" in kwargs
    :param func:
    :return:
    """
    def wrapper(data,
                set_file_title=True,
                set_name_title=False,
                *args,
                **kwargs):
        # set the title of the plot to be the file name or
        # period name if needed
        if set_file_title:
            kwargs["title"] = kwargs["fname"].stem
        if set_name_title:
            kwargs["title"] = kwargs["fname"].stem + "_" + data.name
        fig, ax = func(data, *args, **kwargs)
        
        return fig, ax
    
    return wrapper


def draw_sighlines(yval: float,
                   sig_list: list,
                   label_loc_dict: dict,
                   minus_val: float,
                   plus_val: float,
                   curr_ax,
                   **kwargs):
    """
    Draws an hline at the position indicated in the sig list of indexes by
    looking it up in label_loc_dict then drawing a hline at the yval from
    loc mins_val to loc plus_val on curr_ax
    :param yval:
    :param sig_list:
    :param label_loc_dict:
    :param minus_val:
    :param plus_val:
    :param curr_ax:
    :return:
    """
    for xval in sig_list:
        curr_xval = label_loc_dict[xval]
        hxvals = [curr_xval - minus_val, curr_xval + plus_val]
        hxval_axes = curr_ax.transLimits.transform([(hxvals[0], 0),
                                                    (hxvals[1], 0)])
        hxval_axes_val = hxval_axes[:, 0]
        curr_ax.axhline(yval,
                        xmin=hxval_axes_val[0],
                        xmax=hxval_axes_val[1],
                        **kwargs)

def get_xval_dates(curr_xval,
                   minus_val: pd.Timedelta,
                   plus_val: pd.Timedelta,
                   curr_ax):
    """
    Works to get xvals to plot if dates
    :type plus_val: object
    :param sig_list:
    :param minus_val:
    :param plus_val:
    :param curr_ax:
    :return:
    """
    hxvals = [curr_xval - minus_val, curr_xval + plus_val]
    hxvals_num = [mdates.date2num(x) for x in hxvals]
    hxvals_transformed = curr_ax.transLimits.transform(
        [(hxvals_num[0], 0),
         (hxvals_num[1], 0)]
    )
    hxvals_trans_xvals = hxvals_transformed[:, 0]
    
    return hxvals_trans_xvals
    

def get_xtick_dict(curr_ax):
    """
    Returns a dict of the locations of where each label is
    Can then be used to find where to draw liens
    :param curr_ax:
    :return:
    """
    labels = curr_ax.get_xticklabels()
    locs = curr_ax.get_xticks()
    label_text = [x.get_text() for x in labels]
    label_loc_dict = dict(zip(label_text, locs))
    return label_loc_dict


def sig_locs_get(df: pd.DataFrame,
                 sig_col: str = "p-tukey",
                 sig_val: float = 0.05,
                 index_level2val: int = 0,
                 index_levelget: int=0,
                 test_efsize: bool=True,
                 test_col: str = "efsize",
                 test_val: float=np.inf):
    """
    Finds where the sig_col is less than the sig_val for the index_level2val
    Used for a posthoc tukeys df as example where 0 =baseline-disrupted
    1=baseline-recovery etc.
    :param df:
    :param sig_col:
    :param sig_val:
    :param index_level2val:
    :return:
    """
    sig_mask = df[sig_col] < sig_val
    sig_vals = df[sig_mask]
    if test_efsize:
        test_mask = ~sig_vals['efsize'].isin([test_val, -test_val])
        sig_vals = sig_vals[test_mask]
    sig_index = sig_vals.loc[idx[:, index_level2val], :
                ].index.get_level_values(index_levelget)
    
    return sig_index


def sig_line_coord_get(curr_ax,
                       sig_line_ylevel: float = 0.9):
    """
    Finds the sig_line_level in axes co-ordinates
    :param curr_ax:
    :param sig_line_ylevel:
    :return:
    """
    axes_to_data = curr_ax.transLimits.inverted()
    ycoords = (0.5, sig_line_ylevel)
    ycoords_data = axes_to_data.transform(ycoords)
    ycoord_data_val = ycoords_data[1]
    
    return ycoord_data_val

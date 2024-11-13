# Trying to get actogram plotting as a function for a subplot


# questions - how create this? problem with current set up and decorators
# which work for when the plot is the entire thing, but if just a subplot,
# don't want any of the decorators. Have mostly if statements to determine
# whether to put them in or not.
# Plan - try adding in false statement for * all * decorator kwargs

# imports
from actiPy.actogram_plot import *
from actiPy.plots import multiple_plot_kwarg_decorator, set_title_decorator
import actiPy.preprocessing as prep
import pandas as pd
import numpy as np
import pathlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/07_python_package/"
                   "actiPy")


# define the plotting functions
def _actogram_plot_from_df(data,
                           animal_number,
                           LDR=-1,
                           period="24H",
                           drop_level=True,
                           *args,
                           **kwargs):
    """
    Function to apply LDR remap, then split the dataframe
    according to the given period, then plot the actogram
    :param data: dataframe of activity data
    :param animal_number: which column to plot
    :param LDR: which column has the light data
    :param args:
    :param kwargs:
    :return:
    """

    # remap the light data
    data_LDR_remap = prep.remap_LDR(data, drop_level=drop_level, **kwargs)

    if drop_level:
        # remove top level of the index
        data_LDR_remap.index = data_LDR_remap.index.droplevel(0)

    # split the dfs
    split_df_list = prep.split_entire_dataframe(data_LDR_remap,
                                                period=period)
    # plot with actogram
    _actogram_plot(split_df_list,
                   animal_number=animal_number,
                   LDR=LDR,
                   *args,
                   **kwargs)


@set_title_decorator
@multiple_plot_kwarg_decorator
def _actogram_plot(data,
                   animal_number=0,
                   LDR=-1,
                   ylim=[0, 120],
                   fig=False,
                   subplot=False,
                   **kwargs):
    """
    Function to take in dataframe and plot a double-plotted actogram
    with lights shaded in
    :param data:
    :param animal_number:
    :param LDR:
    :param kwargs:
    :return:
    """

    # select the correct data
    data_to_plot = data[animal_number].copy()
    light_data = data[LDR].copy()

    # set up some constants
    NUM_DAYS = len(data_to_plot.columns)
    linewidth = 1
    if "linewidth" in kwargs:
        linewidth = kwargs["linewidth"]

    # add in values at the start and end
    # to let us double plot effectively
    for data in data_to_plot, light_data:
        data = pad_first_last_days(data)
        # set all 0 values to Nan
        data = convert_zeros(data, -100)

    # if not given a figure, just create the axes
    if not fig:
        fig, ax = plt.subplots(nrows=(NUM_DAYS + 1))
    # create the ax list if given a figure and subplot to do it in.
    else:
        subplot_grid = gs.GridSpecFromSubplotSpec(nrows=(NUM_DAYS + 1),
                                                  ncols=1,
                                                  subplot_spec=subplot,
                                                  wspace=0,
                                                  hspace=0)
        ax = []
        for grid in subplot_grid:
            sub_ax = plt.Subplot(fig, grid)
            fig.add_subplot(sub_ax)
            ax.append(sub_ax)

    # plot two days on each row
    for day_label, axis in zip(data_to_plot.columns[:-1], ax):
        # get two days of data to plot
        day_data = two_days(data_to_plot, day_label)
        day_light_data = two_days(light_data, day_label)

        # create masked data for fill between to avoid horizontal lines
        fill_data = day_data.where(day_data > 0)
        fill_ldr = day_light_data.where(day_light_data > 0)

        # plot the data and LDR
        axis.fill_between(fill_ldr.index,
                          fill_ldr,
                          alpha=0.5,
                          facecolor="grey")
        axis.plot(day_data, linewidth=linewidth)
        axis.fill_between(fill_data.index,
                          fill_data)

        # need to hide all the axis to make visible
        axis.set(xticks=[],
                 xlim=[day_data.index[0],
                       day_data.index[-1]],
                 yticks=[],
                 ylim=ylim)
        spines = ["left", "right", "top", "bottom"]
        for pos in spines:
            axis.spines[pos].set_visible(False)

    if not fig:
        fig.subplots_adjust(hspace=0)

    # create the y labels for every 10th row
    day_markers = np.arange(0, NUM_DAYS, 10)
    for axis, day in zip(ax[::10], day_markers):
        axis.set_ylabel(day,
                        rotation=0,
                        va='center',
                        ha='right')

    # create defaults dict
    params_dict = {
        "xlabel": "Time",
        "ylabel": "Days",
        "interval": 6,
        "title": "Double Plotted Actogram",
    }

    return fig, ax[-1], params_dict


# read in the data file

file_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/01_projects"
                        "/01_thesisdata/04_ageing"
                        "/01_datafiles/01_activity")
file = sorted(file_dir.glob("*.csv"))[0]
df = prep.read_file_to_df(file, index_col=0)

# resample to hourly so can actually work with this data
df_h = df.resample("H").mean()

# try and do a loop with one for each

actogram_kwargs = {
    "drop_level": False,
    "set_file_title": False,
    "linewidth": 0.1,
}

fig, ax = plt.subplots(nrows=3, ncols=2)

for anim, subplot in enumerate(ax.flatten()):
    _actogram_plot_from_df(df_h, anim, fig=fig, subplot=subplot,
                           **actogram_kwargs)

# Plan now? add in a fig keyword so that can take a figure and create the
# subplots from a gridspec from subplot spec

plt.close('all')

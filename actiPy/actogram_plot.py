import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import actiPy.preprocessing as prep
from actiPy.plots import multiple_plot_kwarg_decorator, \
    show_savefig_decorator, set_title_decorator

# function to create actogram plot


def actogram_plot_all_cols(data,
                           fname,
                           LDR=-1,
                           period="24H",
                           *args,
                           **kwargs):
    """
    Function to loop through each column of activity data
    and plot every column except for the LDR
    :param data:
    :param LDR:
    :param period: default "24H"
    :param args:
    :param kwargs: savefig, showfig, fname mainly
    :return:
    """
    # remove LDR column then call actogram plot from
    # df on each remaining column
    # and create new file name for each
    data_with_ldr = data.copy()
    ldr_data = data.pop(data.columns[LDR])

    for animal_no, label in enumerate(data.columns):
        file_name = fname.parent / (fname.stem +
                                    str(animal_no) +
                                    fname.suffix)
        _actogram_plot_from_df(data_with_ldr,
                               animal_number=animal_no,
                               period=period,
                               fname=file_name,
                               *args,
                               **kwargs)


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
    fig, ax = _actogram_plot(split_df_list,
                             animal_number=animal_number,
                             LDR=LDR,
                             *args,
                             **kwargs)

    return fig, ax


@set_title_decorator
@multiple_plot_kwarg_decorator
def _actogram_plot(data,
                   animal_number=0,
                   LDR=-1,
                   ylim=[0, 120],
                   fig=False,
                   subplot=False,
                   ldralpha=0.5,
                   start_day=0,
                   day_label_size=5,
                   **kwargs):
    """
    Plot an double plotted actogram of activity data over several days
    with background shading set by the lights

    Parameters:
    ----------
    data : (pd.DataFrame)
        time-indexed pandas dataframe with activity values in
        columns for each subject and one column for the light levels.
        WRONG - currently expecting list of dataframes, one for each animal
        and single column for each day 
    animal_number : int
        which column number to plot, defaults to 0
    LDR : int
        which columns contains light information, defaults to -1
    ylim : list of two ints
        set the minimum and maximum values to plot
    fig : matplotlib figure object
        Figure to create plot on, if not passed defaults to false and 
        new figure is passed 
    subplot : matplotlib subplot object 
        Subplot from larger figure on which to draw actogram. If not passed
        defaults to False, which requires a fig object to be provided 
    ldralpha : float
        Set the alpha level for how opaque to have the light shading, defaults
        to 0.5
    startday : int
        sets which day to start as day 0 in plot, defaults to 0
    day_label_size : int
        sets size of labels on bottom x axis, defaults to 5

    Returns
    -------
    matplotlib.pyplot.figure
        instance containing overall figure
    matplotlib.pyplot.subplot
        the final subplot so can manipulate for xaxis
    dict
        dict containing plotting kwargs
    """
    # grab line plot constant 
    linewidth = 1
    if "linewidth" in kwargs:
        linewidth = kwargs["linewidth"]

    # select the correct data to plot for activity and light
    col_data = data.columns[animal_number]
    ldr_col = data.columns[LDR]
    data_plot = data.loc[:, col_data].copy()
    data_light = data.loc[:, ldr_col].copy()

    pdb.set_trace()

    # calculate number of days in the data
    days = len(set(data_plot.index.date))
    
    # set all 0 values to be very low so not showing on y index starting at 0
    for data in data_plot, data_light:
        data[data == 0] = -100
    

    # Create figure and subplot for every day

    # error check if not given fig OR subplot 
    if not fig and not subplot:
        raise ValueError("Either 'fig' or 'subplot' must be provided")

    # create a new figure if not passed one when called 
    if not fig:
        fig, ax = plt.subplots(nrows=(days + 1))

    # add subplots to figure if passed when called 
    else:
        subplot_grid = gs.GridSpecFromSubplotSpec(nrows=(days + 1),
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
    for day_label, axis in zip(data_plot.columns[:-1], ax):
        # get two days of data to plot
        day_data = two_days(data_plot, day_label)
        day_data_light = two_days(data_light, day_label)

        # create masked data for fill between to avoid horizontal lines
        fill_data = day_data.where(day_data > 0)
        fill_ldr = day_data_light.where(day_data_light > 0)

        # plot the data and LDR
        axis.fill_between(fill_ldr.index,
                          fill_ldr,
                          alpha=ldralpha,
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
    day_markers = np.arange(0, days, 10)
    day_markers = day_markers + start_day
    for axis, day in zip(ax[::10], day_markers):
        axis.set_ylabel(day,
                        rotation=0,
                        va='center',
                        ha='right',
                        fontsize=day_label_size)

    # create defaults dict
    params_dict = {
        "xlabel": "Time",
        "ylabel": "Days",
        "interval": 6,
        "title": "Double Plotted Actogram",
        "timeaxis": True,
    }

    # put axis as a controllable parameter
    if "timeaxis" in kwargs:
        params_dict['timeaxis'] = kwargs["timeaxis"]

    return fig, ax[-1], params_dict


def pad_first_last_days(data):
    """
    pad_first_last_days
    Function to extend data by one day at the start and the end to help
    with double plotting acotgram 

    Parameters 
    ----------
    data : pd.Series
        series with timeindex 

    Returns 
    -------
    pd.Series
        


    :param data:
    :return:
    """
    NUM_BINS = len(data)
    days = len(data.columns)
    # create a day of 0s and put at the start and the end
    zeros = np.zeros(NUM_BINS)
    data.insert(0, -1, zeros)
    data.insert((days + 1), (days), zeros)
    return data


def convert_zeros(data, value):
    """
    Simple function to turn 0s into nans
    to make plotting look better
    as no line running along x axis
    :param data:
    :return:
    """
    data[data == 0] = value
    return data


def two_days(data, day_one_label):
    """
    gets column of day label and day
    label plus one and returns the values
    as an array
    :param data:
    :param day_one_label:
    :return:
    """
    # get two days as a dataframe

    # grab the values of the first two days
    day_no = data.columns.get_loc(day_one_label)
    day_one = data.iloc[:, day_no]
    day_two = data.iloc[:, (day_no + 1)]

    day_two.index = day_one.index + pd.Timedelta("1D")

    two_days = pd.concat([day_one, day_two])
    return two_days

#     How is this going to work? Needs the full df
#  so can take in the LDR data as well so
# then add in a day of 0s at the start and the end
# to make the first and the final day tidy
# then plot two days at a time

# Alternative is to take in the split list - and make sure t
# that the LDR is also split
# select based on the number in the list


# Function to plot actogram
# want to create split dataframe
# then try imshow?
# or plot.subplots?

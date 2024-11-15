import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import actiPy.preprocessing as prep


@prep.plot_kwarg_decorator
def plot_actogram(data,
                  animal_number=0,
                  LDR=-1,
                  ylim=[0, 120],
                  fig=False,
                  subplot=False,
                  ldralpha=0.5,
                  start_day=0,
                  day_label_size=5,
                  linewidth=0.5,
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
        Set the alpha level for how opaque to have the light shading,
        defaults to 0.5
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
    if "linewidth" in kwargs:
        linewidth = kwargs["linewidth"]

    # check if data is empty 
    if data.empty:
        raise ValueError("Input Dataframe is empty. Cannot plot actogram")

    # select the correct data to plot for activity and light
    col_data = data.columns[animal_number]
    ldr_col = data.columns[LDR]
    data_plot = data.loc[:, col_data].copy()
    data_light = data.loc[:, ldr_col].copy()

    # add entire day of 0s at start and end by extending index
    # grab values from current index
    freq = pd.infer_freq(data_plot.index)
    start = data_plot.index.min()
    end = data_plot.index.max()

    # Extend the range by 24 hours on either side
    extended_start = start - pd.Timedelta(hours=24)
    extended_end = end + pd.Timedelta(hours=24)

    # create new index and set data to it
    extended_index = pd.date_range(
        start=extended_start, end=extended_end, freq=freq)
    data_plot = data_plot.reindex(extended_index, fill_value=-100)

    # select just the days
    days = data_plot.index.normalize().unique()

    # set all 0 values to be very low so not showing on y index starting at 0
    for mask in data_plot, data_light:
        mask[mask == 0] = -100

    # Create figure and subplot for every day
    # create a new figure if not passed one when called
    if not fig:
        fig, ax = plt.subplots(nrows=(len(days) - 1))

    # add subplots to figure if passed when called
    else:
        subplot_grid = gs.GridSpecFromSubplotSpec(nrows=(len(days) - 1),
                                                  ncols=1,
                                                  subplot_spec=subplot,
                                                  wspace=0,
                                                  hspace=0)
        ax = []
        for grid in subplot_grid:
            sub_ax = plt.Subplot(fig, grid)
            fig.add_subplot(sub_ax)
            ax.append(sub_ax)

    # select each day to then plot on separate axis
    # plot two days on each row
    for day_label, axis in zip(days, ax):
        # get two days of data to plot
        curr_day = str(day_label.date())
        next_day = str(day_label.date() + pd.Timedelta("1d"))
        curr_data = data_plot.loc[curr_day:next_day]
        curr_data_light = data_light.loc[curr_day:next_day]

        # create masked data for fill between to avoid horizontal lines
        fill_data = curr_data.where(curr_data > 0)
        fill_ldr = curr_data_light.where(curr_data_light > 0)

        # plot the data and LDR
        axis.fill_between(fill_ldr.index,
                          fill_ldr,
                          alpha=ldralpha,
                          facecolor="grey")
        axis.plot(curr_data, linewidth=linewidth)
        axis.fill_between(fill_data.index,
                          fill_data)

        # need to hide all the axis to make visible
        axis.set(xticks=[],
                 xlim=[curr_data.index[0],
                       curr_data.index[-1]],
                 yticks=[],
                 ylim=ylim)
        spines = ["left", "right", "top", "bottom"]
        for pos in spines:
            axis.spines[pos].set_visible(False)

    if not fig:
        fig.subplots_adjust(hspace=0)

    # create the y labels for every 10th row
    day_markers = np.arange(0, len(days), 10)
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

    return fig, ax, params_dict

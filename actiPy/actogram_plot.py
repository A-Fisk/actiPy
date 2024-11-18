import re
import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import actiPy.activity as act
import actiPy.preprocessing as prep


@prep.plot_kwarg_decorator
def plot_actogram(data,
                  subject_no=0,
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
    subject_no : int
        which column number to plot, defaults to 0
    LDR : int
        which columns contains light information, defaults to -1
    ylim : list of two ints
        set the minimum and maximum values to plot
    fig : matplotlib figure object
        Figure to create plot on, if not passed defaults to false and
        new figure is passed
    subplot : matplotlib subplotspec object
        Subplotspec from larger figure on which to draw actogram.
        Must be created from gridspec
        If not passed
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
    col_data = data.columns[subject_no]
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


@prep.validate_input
@prep.plot_kwarg_decorator
def plot_activity_profile(data,
                          col=0,
                          light_col=-1,
                          subplot=None,
                          resample=False,
                          resample_freq="h",
                          *args,
                          **kwargs):
    """
    Plot the activity profile with mean and SEM (Standard Error of the Mean).
    Optionally resample the data before plotting.

    Parameters
    ----------
    data : pd.DataFrame or pd.Series
        Activity data indexed by time. If `data` is a DataFrame, the
        function uses the column specified by `col` (default is the
        first column).
    col : int, optional
        The index of the column to plot, used when `data` is a
        DataFrame (default is 0).
    subplot : matplotlib.axes._axes.Axes, optional
        Subplot to plot on. If None, a new figure and axis are
        created (default is None).
    resample : bool, optional
        Whether to resample the data before plotting.
        If `True`, the data will be resampled to the frequency
        specified by `resample_freq` (default is `False`).
    resample_freq : str, optional
        The frequency to resample the data to.
        This can be any valid pandas offset string
        (e.g., "h" for hourly, "min" for minutely).
        The default is "h" (hourly).
    *args, **kwargs : additional arguments
        These are passed to the plotting function,
        such as `timeaxis` to control the appearance of the x-axis.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the plot.
    ax : matplotlib.axes._axes.Axes
        The axis with the plot.
    params_dict : dict
        A dictionary containing the plot's parameters,
        including labels, title, and xlim.
    """
    # ability to resample if required
    if resample:
        data = data.resample(resample_freq).mean()

    # select just the subject
    curr_data = data.iloc[:, col]
    light_data = data.iloc[:, light_col]

    # Calculate mean activity and SEM
    mean, sem = act.calculate_mean_activity(curr_data, sem=True)
    light_mean = act.calculate_mean_activity(light_data)

    # Convert the index of mean and sem to a DatetimeIndex starting 2001-01-01
    start_date = "2001-01-01"
    freq = pd.infer_freq(data.index)
    datetime_index = pd.date_range(
        start=start_date, periods=len(mean), freq=freq)
    mean.index = datetime_index
    sem.index = datetime_index
    light_mean.index = datetime_index

    # Check if there is a number in the frequency string using regex
    if re.search(r'\d', freq):  # If there's a number, use the frequency as is
        freq = pd.Timedelta(freq)
    else:  # If there's no number, prepend "1" to the frequency
        freq = pd.Timedelta("1" + freq)  # Prepend '1' to the frequency
    # Extend the light_mean data by one extra period and forward fill
    light_mean = pd.concat([light_mean, pd.Series(
        [light_mean.iloc[-1]], index=[light_mean.index[-1] + pd.Timedelta(freq)])])
    light_mean.ffill(inplace=True)

    # Offset the mean and sem data to plot in the middle of the hour
    offset_time = 0.5 * pd.Timedelta(freq)
    mean.index += offset_time
    sem.index += offset_time
    light_mean.index += offset_time

    # Create plot if no subplot is provided
    if subplot is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = plt.gcf()
        ax = subplot

    # Plot the mean line
    ax.plot(
        mean.index, mean, label="Mean Activity", color="blue", linewidth=2)

    # Add shaded SEM region
    ax.fill_between(
        mean.index,
        mean - sem,
        mean + sem,
        color="blue",
        alpha=0.3,
        label="± SEM"
    )

    # get ylims to set at this level later
    ylim = ax.get_ylim()

    # Find the min and max of light_mean
    min_light_mean = light_mean.min()
    max_light_mean = light_mean.max()

    # Define the target range
    target_max = 10 * ylim[1]
    target_min = -1 * target_max

    # Scale the light_mean values to the target range
    # The formula to scale the values is:
    # scaled_value = (value - min_value) / (max_value - min_value)
    # * (target_max - target_min) + target_min

    scaled_light_mean = (light_mean - min_light_mean \
                         ) / (max_light_mean - min_light_mean \
                         ) * (target_max - target_min) + target_min

    # Add lights region
    ax.fill_between(
        scaled_light_mean.index,
        scaled_light_mean,
        color='grey',
        alpha=0.2
    )
    
    # Add labels, legend, and title
    ax.set_xlabel("Time")
    ax.set_ylabel("Activity")
    ax.set_ylim(ylim)
    ax.set_title("Activity Profile with Mean and SEM")
    ax.legend()

    # create defaults dict
    xlim = [mean.index[0], (mean.index[0] + pd.Timedelta("24h"))]
    params_dict = {
        "xlabel": "Time",
        "ylabel": "Activity",
        "interval": 6,
        "title": "Mean activity profile",
        "timeaxis": True,
        "xlim": xlim,
    }

    # put axis as a controllable parameter
    if "timeaxis" in kwargs:
        params_dict['timeaxis'] = kwargs["timeaxis"]

    return fig, ax, params_dict

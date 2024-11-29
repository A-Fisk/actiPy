# Scripts for finding episodes
# can be sleep or activity episodes!

import pdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.core.debugger import set_trace
import circaPy.preprocessing as prep

# function to create episode dataframe
# starting off by working on just a single
# column.
# take in dataframe and column number as args
# and then return a series <- later problem
# to loop over and do for everything in the
# df


@prep.validate_input
def find_episodes(data,
                  subject_no=0,
                  min_length="1s",
                  max_interruption="0s",
                  *args,
                  **kwargs):
    """
    Identifies episodes in a time series of activity data for a specific subject,
    optionally merging episodes if interruptions between them are below a given
    threshold.

    Parameters
    ----------
    data : pd.DataFrame
        The activity data for multiple subjects, where each column represents
        a subject's activity over time, and the index is a time-based index.
    subject_no : int, optional
        The column index of the subject to analyze. Default is 0.
    min_length : str or pandas.Timedelta, optional
        The minimum duration for an episode to be included in the results.
        Can be specified as a string (e.g., "1s", "5m") or a `pandas.Timedelta`
        object.  Default is "1s".
    max_interruption : str or pandas.Timedelta, optional
        The maximum allowable interruption between episodes for them to be
        considered a single episode. If the interruption is below this threshold,
        the episodes are merged. Can be specified as a string (e.g., "1s", "5m")
        or a `pandas.Timedelta` object. Default is "0s" (no merging).
    *args : tuple
        Additional positional arguments passed to downstream filtering functions.
    **kwargs : dict
        Additional keyword arguments passed to downstream filtering functions.

    Returns
    -------
    pandas.Series
        A Series where the index represents the start time of valid episodes,
        and the values represent the duration of each episode in seconds.

    Examples
    --------
    >>> import pandas as pd
    >>> import numpy as np
    >>> index = pd.date_range("2024-01-01", periods=100, freq="1s")
    >>> data = pd.DataFrame({
    ...     "Subject 1": np.random.choice([0, 1], size=100, p=[0.8, 0.2]),
    ...     "Subject 2": np.random.choice([0, 1], size=100, p=[0.7, 0.3]),
    ... }, index=index)
    >>> find_episodes(data, subject_no=0, min_length="3s", max_interruption="2s")
    2024-01-01 00:00:15    7.0
    2024-01-01 00:00:45    5.0
    dtype: float64
    """
    # select single column
    curr_data = data.iloc[:, subject_no]

    # Determine the threshold for episode identification
    zero_data = (curr_data == 0)
    episode_data = curr_data[zero_data]

    # Identify the time differences between consecutive points
    shifted_index = episode_data.index.to_series().shift(-1)  # Shift index forward
    episode_durations = (
        shifted_index - episode_data.index.to_series()
    ).dropna().dt.total_seconds()

    # Filter out consecutive zero episodes (treat them as one episode)
    # where goes activity to 0
    episode_ends = zero_data & ~zero_data.shift(1, fill_value=False)
    # where goes from 0 to activity
    episode_starts = zero_data & ~zero_data.shift(-1, fill_value=False)
    # grab the start and end times
    data_freq = pd.Timedelta(pd.infer_freq(curr_data.index))
    episode_start_times = curr_data.index[episode_starts] + data_freq
    episode_end_times = curr_data.index[episode_ends]

    # Create a DataFrame with episodes
    episode_df = pd.Series(
        (episode_end_times[1:] - episode_start_times[:-1]).total_seconds(),
        index=episode_start_times[:-1])

    # Merge episodes based on max_interruption
    if max_interruption != "0s":
        max_interruption_td = pd.Timedelta(max_interruption)
        merged_episodes = []
        current_start = None
        current_end = None

        # go through each start time and duration
        for start_time, duration in episode_df.items():
            if current_start is None:
                current_start = start_time
                current_duration = duration
            else:
                # check what the interruption length is between this and last
                interruption = (
                    start_time - (
                        current_start + pd.Timedelta(
                            seconds=current_duration)
                    )
                ).total_seconds()
                # if short enough
                if interruption <= max_interruption_td.total_seconds():
                    # Merge episodes
                    current_duration += interruption + duration
                else:
                    # save current episode and start new one
                    merged_episodes.append((current_start, current_duration))
                    current_start = start_time
                    current_duration = duration

        # Append the last episode
        if current_start is not None:
            merged_episodes.append((current_start, current_duration))

        # Update the episode DataFrame
        episode_df = pd.Series(
            {start: duration for start, duration in merged_episodes})

    # Finally, filter episodes by min_length
    min_length_td = pd.Timedelta(min_length)
    episode_df = episode_df[episode_df >= min_length_td.total_seconds()]

    return episode_df


def _episode_finder(data,
                    inactive_episodes=False,
                    allow_interruptions=False,
                    *args,
                    **kwargs):
    """
    _episode_finder

    Returns a Series containing all the episodes in the given
    data, with the index indicating start time and value indicating
    duration.

    Params:
    data:
        pd.Series. raw activity data to find episode in
    inactive_episodes:
        Boolean, default False.
        If False, finds activity episodes (where value > 0)
        If True, finds inactive episodes (value == 0)
    allow_interruptions:
        Boolean, default False
        Whether to filter for episode interruptions by calling
        filter_episodes function

    Returns:
        pd.Series. Index is start of episode and value is duration

    """

    # find all the zeros in the data
    # get the timedeltas between them
    # remove all those where 0-0 with
    # nothing in between
    # save them as a series with the
    # length of each episode in the
    # start-time of the index

    # find all the zeros in the data
    data_zeros = data[data == 0]
    if inactive_episodes:
        data_zeros = data[data > 0]

    # get the timedeltas between them
    data_zeros_shift = data_zeros[1:]
    episode_lengths = (data_zeros_shift.index -
                       data_zeros.index[:-1]).total_seconds()
    # create Series with the start times
    start_times = data_zeros.index[:-1]
    episode_series = pd.Series(episode_lengths,
                               index=start_times)
    # filter out all those with no values between
    # the zeros
    # find the unit of time - assuming stationary
    basic_time_unit = data.index[1] - data.index[0]
    extended_time_unit = ((2 * basic_time_unit) -
                          pd.Timedelta("1s")).total_seconds()
    if "min_length" in kwargs:
        extended_time_unit = pd.Timedelta(kwargs["min_length"]).total_seconds()
    episode_lengths_filtered = episode_series[
        episode_series > extended_time_unit
    ]
    # label it with the correct name
    name = data.name
    episode_lengths_filtered.name = name

    if allow_interruptions:
        episode_lengths_filtered = filter_episodes(
            data, episode_lengths_filtered, **kwargs)

    return episode_lengths_filtered


def filter_episodes(
        raw_data,
        episode_data,
        length_val: str = "10s",
        intensity_val: int = 30,
        **kwargs):
    '''
    Episode filter

    Returns a dataframe of episodes where the duration and intensity
    of an interruption is shorter than and less than the given values
    respectively

    param:
    raw_data:
        original activity dataframe
    episode_data:
        raw episodes from activity dataframe
    length_val:str "10s"
        interruption time to allow, as a timedelta string
    intensity_val:int 30
        max interruption intensity to allow

    returns:
    pandas DataFrame
        Index is start of episode and value is duration of episode
        in seconds
    '''

    # find start of each episodes
    start_index = episode_data.index[:-1]
    start_index_next = episode_data.index[1:]

    # find lengths of interruptions
    time_between_episodes = (start_index_next - start_index).total_seconds()
    durations = episode_data.values[:-1]

    # find locations where interruption is shorter than value
    filter_length = pd.Timedelta(length_val).total_seconds()
    duration_plus_filter = durations + filter_length
    locations = duration_plus_filter > time_between_episodes

    # find where interruption value is below given value
    max_values = [raw_data.loc[x:y].max()
                  for x, y in zip(start_index, start_index_next)]
    max_mask = np.array([x > intensity_val for x in max_values])

    # filter for given length and intensity interruption
    episodes_filtered = episode_data.iloc[
        :-1][locations & max_mask]

    # Add the duration of skipped episode to the main episode
    start_list = episodes_filtered.index[0:-1]
    end_list = episodes_filtered.index[1:] - pd.Timedelta("1s")
    new_durations = [episode_data.loc[x:y].sum() for
                     x, y in zip(start_list, end_list)]
    new_durations.append(episodes_filtered.iloc[-1])
    episodes_filtered.iloc[:] = new_durations

    return episodes_filtered


def episode_find_df(data,
                    LDR=-1,
                    remove_lights=True,
                    check_max=True,
                    *args,
                    **kwargs):
    """
    Episode_find_df

    Returns a dataframe with found episodes for each column.
    Applies _episode_finder in turn to each column and then
    concatenates them into a single dataframe

    Params:
    data:
        pd.DataFrame. Dataframe of activity data to find
        episodes in
    remove_lights:
        Boolean. Default True.
        If true, drops the LDR column
    LDR:
        int, default -1. Column number to remove if lights
        included in dataframe and removing lights
    check_max:
        Boolean, default True.
        If true, passes to check_episode_max to see if any
        episodes are longer than a given max

    Returns:
        pd.Dataframe
        Dataframe with same columns as original, index indicates
        start of episode and value indicates duration in seconds.
    """

    # loop through each column
    # and find the episodes in that column

    # remove light column
    if remove_lights:
        ldr_data = data.iloc[:, LDR].copy()
        ldr_label = data.columns[LDR]

    # find episodes for each animal
    episode_series_list = []
    for col in data:
        data_series = data.loc[:, col]
        col_episodes = _episode_finder(data_series, *args, **kwargs)
        episode_series_list.append(col_episodes)
    episode_df = pd.concat(episode_series_list, axis=1)

    # put light column back in
    if remove_lights:
        episode_df[ldr_label] = ldr_data

    # check that we are getting reasonable episode lengths
    if check_max:
        try:
            check_episode_max(episode_df)
        except BaseException:
            episode_df = episode_df.iloc[:-1, :]
        check_episode_max(episode_df, **kwargs)

    return episode_df


def check_episode_max(data,
                      max_time="6h",
                      LDR=-1,
                      **kwargs):
    """
    Simple function to raise value error if any of the
    values are over 6 hours long
    :param data:
    :return:
    """
    comparison = pd.Timedelta(max_time).total_seconds()
    # grab the max values from all non-LDR columns
    max_values = data.max()
    max_values.pop(data.columns[LDR])
    if any(max_values > comparison):
        raise ValueError("Max episode longer than %s" % max_time)

# Functions to plot histogram of data


def _deprec_episode_histogram(data,
                              fig=None,
                              ax=None,
                              LDR=-1,
                              convert=False,
                              log=True,
                              **kwargs):
    """
    Function to take dataframe and plot each pir as a
    separate column
    :param data:
    :param LDR:
    :param args:
    :param kwargs:
    :return:
    """
    # preprocess to be able to plot easily
    data.dropna(inplace=True)
    if convert:
        data = convert_data_to_unit(data)

    # create figure if not given
    if not fig and not ax:
        no_animals = len(data.columns)
        fig, ax = plt.subplots(nrows=1,
                               ncols=no_animals,
                               sharex=True,
                               sharey=True)

    # plot a histogram on the axis
    for axis, col in zip(ax, data.columns):
        axis.hist(data.loc[:, col])
        if log:
            axis.set_yscale('log')
        axis.set_title(col)

    # set the defaults
    params_dict = {

    }


def episode_histogram(data_list,
                      LDR: int = -1,
                      logx: bool = True,
                      clip: bool = True,
                      **kwargs):
    """
    Plotting function takes in df and separates into list and plots
    :param data_list:
    :param LDR:
    :param kwargs:
    :return:
    """

    # remove LDR from all dfs in the list and put in label
    tidied_data_list = [x.drop(x.columns[LDR], axis=1) for x in data_list]
    label_list = [x.name for x in data_list]
    no_animals = len(tidied_data_list[0].columns)
    no_conditions = len(tidied_data_list)

    # set some function constants
    bins = 10
    if "bins" in kwargs:
        bins = kwargs["bins"]

    logy = False
    if "logy" in kwargs:
        logy = kwargs["logy"]

    # plot the data, each condition separate row, each animal on a column
    fig, ax = plt.subplots(nrows=no_conditions,
                           ncols=no_animals,
                           sharex=True,
                           sharey=True)
    # plot each condition on a separate row
    for row, condition in enumerate(label_list):
        plotting_df = tidied_data_list[row]
        for col_plot, col_label in enumerate(plotting_df):
            plotting_col = plotting_df.loc[:, col_label].dropna()
            if clip and "bins" in kwargs:
                plotting_col = np.clip(plotting_col, 0, bins[-1])
            if no_animals > 1:
                curr_axis = ax[row, col_plot]
            else:
                curr_axis = ax[row]
            curr_axis.hist(plotting_col,
                           bins=bins,
                           log=logy,
                           density=True)
            if row == 0:
                curr_axis.set_title(col_label)
            if col_plot == 0:
                curr_axis.set_ylabel(condition)
            if logx:
                curr_axis.set_xscale('log')

    # tidy up the subplots
    fig.subplots_adjust(hspace=0,
                        wspace=0)

    # set the default values
    params_dict = {
        "xlabel": "Episode Duration, seconds",
        "ylabel": "Normalised Density",
        "title": "Episode histogram"
    }

    return fig, curr_axis, params_dict


def convert_data_to_unit(data,
                         unit_time="1M"):
    """
    Function to convert all the values from seconds to specified
    unit
    :param data:
    :param unit_time:
    :return:
    """

    conversion_amount = pd.Timedelta(unit_time).total_seconds()
    data_new = data.copy() / conversion_amount
    return data_new


def _stack_all_values(data):
    """
    gets all values for all animals in a single column
    :param data:
    :return:
    """
    # create long dataframe with values for all animals in it
    df_long = data.stack()
    df_long.index = df_long.index.droplevel(2)
    df = pd.DataFrame(df_long)

    df.columns = ["Sum of all animals"]
    df.name = data.name

    return df

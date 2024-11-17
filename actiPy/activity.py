import pdb
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import actiPy.preprocessing as prep
idx = pd.IndexSlice


def calculate_IV(data):
    """
    Intradavariability calculation.

    Calculates intradayvariabaility according to the equation set out in
    van Someren et al 1996, a ratio of variance of the first derivative
    to overall variance of the data.
    IV = n * sum{i=2 -> n}(x{i} - x{i-1})**2
                        /
        (n-1) * sum{i=1 -> n}(x{i} - x{bar})**2

    Parameters
    ----------
    data : array or dataframe
        Timeseries data to calculate.

    Returns
    -------
    array or dataframe with calculated IV variables
    """
    # Convert to numpy array for convenience
    x = np.array(data)
    n = len(x)

    if n < 2:
        raise ValueError(
            "At least two data points are required to compute IV.")

    # Calculate mean of x
    x_mean = np.mean(x)

    # Calculate numerator
    numerator = n * np.sum((x[1:] - x[:-1])**2)

    # Calculate denominator
    denominator = (n - 1) * np.sum((x - x_mean)**2)

    # Compute IV
    IV = numerator / denominator
    return IV


def calculate_mean_activity(data):
    """
    Mean activity calculation

    Calculates the mean activity at each time point for all days.

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame with a datetime index and activity values for each time
        point.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the mean activity at each time point across all
        days.
    """
    if data.empty:
        raise ValueError("The input DataFrame is empty.")

    if not isinstance(data.index, pd.DatetimeIndex):
        raise TypeError("The DataFrame must have a DatetimeIndex.")

    # Group data by time of day (ignoring the date) and calculate the mean for
    # each time point
    mean_activity = data.groupby(data.index.time).mean()

    # Convert the time index back to datetime for clarity
    mean_activity.index = pd.to_datetime(
        mean_activity.index, format="%H:%M:%S").time

    return mean_activity


def _drop_ldr_decorator(func, ldr_col=-1):
    """
    Function to drop values from ldr col
    :param func:
    :return:
    """
    def wrapper(data, **kwargs):

        # call function
        new_data = func(data, **kwargs)

        # remove ldr values
        ldr_label = new_data.columns[ldr_col]
        new_data.drop(ldr_label, axis=1, inplace=True)

        return new_data

    return wrapper


def _day_count(data):
    """Returns number of whole days in the index"""
    data = data.reset_index(0, drop=True)
    time_of_data = (data.index[-1] - data.index[0])
    day_count = time_of_data.days

    # if over 20 hours, count as another full day
    hours = time_of_data.components.hours
    if hours > 20:
        day_count = day_count + 1

    return day_count


# count number of days <- whole days what we care about?, or hours?
@_drop_ldr_decorator
def sum_per_day(data,
                label="light_period",
                **kwargs):
    """Function to compute sum of data normalised to number of days"""
    # divide activity sum by number of days
    days = data.groupby(label).apply(_day_count)
    sum = data.groupby(label).sum()
    sum_per_day = sum.div(days, axis=0)

    return sum_per_day


@_drop_ldr_decorator
def count_per_day(data,
                  label='light_period',
                  convert=True,
                  **kwargs):
    """ Function to count number of active bins - gives time per day """

    # divide acitivity *count* by number of days
    days = data.groupby(label).apply(_day_count)

    # need to count number of non-0 values
    bool_df = data.fillna(0).astype(bool)
    count = bool_df.groupby(label).sum()
    count_per_day = count.div(days, axis=0)

    # convert to hours if asked
    if convert:
        count_per_day = prep._convert_to_units(count_per_day, **kwargs)

    return count_per_day


def pointplot_from_df(data,
                      groups='',
                      **kwargs):
    """
    Function to take in data, rename the axis as required, turn into longform
    data and do a pointplot
    :param data:
    :param kwargs:
    :return:
    """

    # turn into longform data
    longform_df = _longform_data(data)
    longform_df.rename(columns={0: data.name}, inplace=True)

    # pointplot
    _point_plot(longform_df,
                groups='group',
                ylevel=data.name,
                **kwargs)


def _longform_data(data, **kwargs):

    plotting_data = data.iloc[:, :-1].stack().reset_index()

    return plotting_data


def _point_plot(data,
                xlevel='',
                ylevel='',
                groups='',
                **kwargs):
    """

    :param data:
    :param xlevel:
    :param ylevel:
    :param hue:
    :param kwargs:
    :return:
    """
    fig, ax = plt.subplots()
    sns.pointplot(x=xlevel, y=ylevel, hue=groups, data=data, ax=ax,
                  **kwargs)

    params_dict = {
        "timeaxis": False,
        "title": ylevel,
        "xlabel": "light_period",
    }

    return fig, ax, params_dict


# TODO: Remove redundant by group function


def iv_by_group(data,
                level: int = 0):
    """
    Finds iv by day for each level of axis
    :param data:
    :param level:
    :return:
    """
    iv = data.groupby(level=level).apply(_intradayvar)

    return iv


def catplot(data, **kwargs):
    """
    Function to flatten input data and plot with scatter and line plot
    :param data:
    :param kwargs:
    :return:
    """
    fig, ax = plt.subplots()

    import seaborn as sns
    sns.set()

    plot = data.stack().reset_index()
    plot.rename(columns={0: data.name}, inplace=True)

    xlevel = plot.columns[0]
    ylevel = plot.columns[-1]

    sns.stripplot(data=plot, x=xlevel, y=ylevel, color="k", ax=ax)
    sns.pointplot(data=plot, x=xlevel, y=ylevel, color="k",
                  capsize=0.2, join=False,
                  errwidth=1, ax=ax)

    params_dict = {
        "timeaxis": False,
        "title": data.name,
        "xlabel": False,
        "ylabel": False,
    }

    return fig, ax, params_dict


def normalise_to_baseline(data,
                          level_conds: int = 0,
                          level_period: int = 1,
                          baseline_level: int = 0,
                          disrupted_level: int = 1,
                          ldr_col: int = -1):
    """
    Normalises each level of level_conds to it's own baseline
    :param data:
    :param level_conds:
    :param level_period:
    :return:
    """
    idx = pd.IndexSlice
    vals = data.index.get_level_values(level_conds).unique()
    cond_dict = {}
    for val in vals:
        temp_df = data.loc[val]
        temp_norm = (temp_df / temp_df.iloc[baseline_level]) * 100
        cond_dict[val] = temp_norm
    norm_df = pd.concat(cond_dict)

    cond_vals = data.index.get_level_values(level_period).unique()
    disrupted_with_light = norm_df.loc[idx[:,
                                           cond_vals[disrupted_level], :], :]
    disrupted_nolight = disrupted_with_light.iloc[:, :ldr_col]

    disrupted_nolight.index.rename("Condition", level=0, inplace=True)

    return disrupted_nolight


# TODO test for count per day
def light_phase_activity_nfreerun(test_df,
                                  ldr_label: str = "LDR",
                                  ldr_val: float = 150):
    light_mask = test_df.loc[:, ldr_label] > ldr_val
    light_data = test_df[light_mask]
    light_sum = light_data.sum()
    total_sum = test_df.sum()
    light_phase_activity = (light_sum / total_sum) * 100

    return light_phase_activity


def light_phase_activity_freerun(test_df,
                                 start_light="2010-01-01 00:00:00",
                                 end_light="2010-01-01 12:00:00"):
    light_data = test_df.loc[idx[:, :, :, start_light:end_light], :]
    light_sum = light_data.sum()
    total_sum = test_df.sum()
    light_phase_activity = light_sum / total_sum

    return light_phase_activity


def relative_amplitude(test_df):
    hourly_max = test_df.max()
    hourly_min = test_df.min()
    hourly_diff = hourly_max - hourly_min
    hourly_sum = hourly_max + hourly_min
    relative_amplitude = hourly_diff / hourly_sum

    return relative_amplitude


def hist_vals(test_data, bins, hist_cols, **kwargs):
    hist = np.histogram(test_data, bins, **kwargs)
    hist_vals = pd.DataFrame(hist[0], index=hist_cols)
    return hist_vals

import pdb
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import actiPy.preprocessing as prep


@prep.validate_input
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

    if numerator == 0 and denominator == 0:
        return 0

    # Compute IV
    IV = numerator / denominator
    return IV


@prep.validate_input
def calculate_mean_activity(data, sem=False):
    """
    Mean activity calculation

    Calculates the mean activity at each time point for all days.

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame with a datetime index and activity values for each time
        point.
    sem: Boolean
        Whether to return standard error of the mean as well, defaults 
        to False 

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the mean activity at each time point across all
        days.
    """
    # Group data by time of day (ignoring the date) and calculate the mean for
    # each time point
    mean_activity = data.groupby(data.index.time).mean()

    # Convert the time index back to datetime for clarity
    mean_activity.index = pd.to_datetime(
        mean_activity.index, format="%H:%M:%S").time
   
    if sem:
        sem_activity = data.groupby(data.index.time).sem()
        sem_activity.index = pd.to_datetime(
                sem_activity.index, format="%H:%M:%S").time
        
        return mean_activity, sem_activity

    return mean_activity


@prep.validate_input
def normalise_to_baseline(data, baseline_data):
    """
    normalise_to_baseline
    Takes two dataframes and expresses the data as a percentage of the
    baseline_data.

    Parameters
    ----------
    data : pd.Series
        Timeindexed data to be normalised
    baseline_data : pd.Series
        Timeindexed data to be normalised against

    returns
    -------
    dataframe
        Timeindexed dataframe with original data as a percentage of
        baseline_data
    """
    # calculate mean activity for baseline
    baseline_mean = calculate_mean_activity(baseline_data)

    # map the mean values to each timepoint
    time_index = data.index.time
    baseline_mean_values = baseline_mean.loc[time_index].values

    # calculate normalised values
    normalised = (data.values / baseline_mean_values) * 100
    norm_series = pd.Series(normalised, index=data.index, name=data.name)

    return norm_series


@prep.validate_input
def light_phase_activity(data,
                         light_col=-1,
                         light_val=150):
    """
    Light_phase_activity
    Calculates the percentage of activity occurring during the light phase
    compared to the total activity in the dataset.

    Parameters
    ----------
    data : pd.DataFrame
        A time-indexed DataFrame containing activity and light data.
    light_col : int, optional
        Index of the column that contains light data.
        Default is -1 (the last column).
    light_val : int, optional
        The threshold above which the light is considered "on". Default is 150.

    Returns
    -------
    pd.Series
        A Series where each element represents the percentage of activity
        occurring during the light phase for each column in the DataFrame.

    Notes
    -----
    - The function assumes the `data` DataFrame contains numeric data.
    - Activity columns should be numeric and summable.
    - If no light values exceed the `light_val` threshold, the returned
      percentage will be 0 for all activity columns.
    - Ensure `data` is not empty and contains the specified `light_col` index.
    """
    # select activity just during light
    light_mask = data.iloc[:, light_col] >= light_val
    light_data = data[light_mask]

    # sum up the activity
    light_sum = light_data.sum()
    total_sum = data.sum()

    # calculate light phase as percentage
    light_phase_activity = (light_sum / total_sum) * 100

    return light_phase_activity


@prep.validate_input
def relative_amplitude(data,
                       time_unit="h",
                       active_time=1,
                       inactive_time=1):
    """
    Relative Amplitude

    Calculates the relative amplitude for each column as the difference between
    the maximum activity during the most active hours and the minimum activity
    during the least active hours, after resampling the data to an hourly
    frequency.

    Parameters
    ----------
    data : pd.DataFrame
        A DataFrame with a time index and activity columns.
    active_time : int, optional
        The number of most active hours to consider. Default is 10.
    inactive_time : int, optional
        The number of least active hours to consider. Default is 5.

    Returns
    -------
    pd.Series
        A Series where the index corresponds to the column names from the
        input data, and the values are the relative amplitude for each column.

    Raises
    ------
    ValueError
        If `active_time` + `inactive_time` exceeds the length of the resampled data.
    """
    # Resample data to the given frequency
    hourly_data = data.resample(time_unit).mean()

    # Check if active_time + inactive_time exceeds the data length
    if active_time + inactive_time > len(hourly_data):
        raise ValueError(
            f"The sum of active_time ({active_time}) and inactive_time"
            f"({inactive_time}) exceeds the length of the resampled "
            f"data ({len(hourly_data)})."
        )
    # Dictionary to store relative amplitude for each column
    relative_amplitudes = {}

    for column in hourly_data.columns:
        # Get the most active hours for this column
        most_active_time = hourly_data[column].nlargest(active_time)

        # Get the least active hours for this column
        least_active_time = hourly_data[column].nsmallest(inactive_time)

        # Calculate max and min activity
        max_active = most_active_time.mean()
        min_inactive = least_active_time.mean()

        # Calculate relative amplitude
        amplitude_diff = max_active - min_inactive
        amplitude_sum = max_active + min_inactive
        relative_amplitudes[column] = amplitude_diff / amplitude_sum

    relative_amplitude = pd.Series(
        relative_amplitudes, name="Relative Amplitude")

    return relative_amplitude

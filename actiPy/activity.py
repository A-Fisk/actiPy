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
        If `active_time` + `inactive_time` exceeds the length of the resampled
        data.
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


@prep.validate_input
def calculate_IS(data, subject_no=0):
    r"""
    Calculates the Interdaily Stability (IS) for a given time series of
    activity data.

    The Interdaily Stability (IS) is a measure of the consistency of an
    activity pattern across different periods of time (e.g., days). It is
    defined as the ratio of variance caused by the time periods to the total
    variance of the data. Higher IS values indicate more stability in the
    activity pattern.

    The formula for IS is:

    .. math::

        IS = \frac{N \sum_{h=1}^p (M_h - M )^2}{p \sum_{i=1}^N (x_i - M)^2}

    where:
        - :math:`N` is the total number of observations.
        - :math:`p` is the number of time points in the period.
        - :math:`M_h` is the mean value at time point :math:`h`.
        - :math:`M` is the overall mean.
        - :math:`x_i` is the value of the observation :math:`i`.

    The result is a ratio of variances that ranges from 0 to 1, where higher
    values indicate a more stable activity pattern. The function calculates the
    variance in the activity time series for each time point relative to the
    overall mean, and compares this to the total variance of the series.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the activity data for multiple subjects, where
        each column represents a subject's data over time.
    subject_no : int, optional
        The column index of the subject for whom the IS is being calculated.
        Default is 0.

    Returns
    -------
    float
        The Interdaily Stability value (IS) for the specified subject's data.

    Notes
    -----
    The function assumes that the data is organized in time series format,
    where each row corresponds to a time point, and each column corresponds to
    a subject's activity data.
    """
    # select the data
    curr_data = data.iloc[:, subject_no]

    # calculate mean
    mean_data = calculate_mean_activity(curr_data)

    # get squared deviation from the mean
    mean = curr_data.mean()
    square_deviation = (mean_data - mean) ** 2

    # divide by mean to get variance around the time points
    time_variance = square_deviation.sum() / len(square_deviation)

    # divide by total variance
    total_variance = curr_data.var()
    interdaily_stability = time_variance / total_variance

    return interdaily_stability


def calculate_TV(data, subject_no=0, period="24h"):
    r"""
    Calculates Timepoint Variability

    The Interdaily Stability is the ratio of variance caused by the period
    to the total variance. It is defined as:

    .. math::

    \begin{equation*}
    TV=
    \frac{\sum_{h=1}^P}{P} \frac{S^2_h}{S^2}
    \end{equation*}


    \begin{equation*}
    TV=
    \frac{\sum_{h=1}^P \frac{\sum_{x=1}^N (x_i-x_h)^2}{N}}{P \frac{\sum_{i=1}^N (x_i - \bar x)^2}{N}}
    \end{equation*}

    \begin{equation*}
    TV=
    \frac{\sum_{h=1}^P \sum_{x=1}^N (x_i-x_h)^2}{P \sum_{i=1}^N (x_i - \bar x)^2}
    \end{equation*}

    where:
        - :math:`N` is the total number of observations.
        - :math:`p` is the number of time points in the period.
        - :math:`M_h` is the mean value at time point :math:`h`.
        - :math:`M` is the overall mean.
        - :math:`x_i` is the value of the observation :math:`i`.

    The TV value ranges from 0 to 1, lower is more stable.
    """
    # select the data
    curr_data = data.iloc[:, subject_no]

    # calculate mean
    mean_data = calculate_mean_activity(curr_data)

    # sum of squares from mean
    # extend mean data so matches length of curr_data
    multiple_length = len(curr_data) / len(mean_data)
    repeated_mean_data = pd.Series(
        np.tile(
            mean_data.values,
            (int(multiple_length) + 1)
        )[:len(curr_data)], index=curr_data.index)

    # calculate differences square of each time point from that timepoint mean
    deviation = repeated_mean_data - curr_data
    square_dev = deviation ** 2

    # group them by time of day
    square_dev.index = square_dev.index.strftime("%H:%M:%S")
    sum_of_squares = square_dev.groupby(square_dev.index).sum()

    # divide by mean to get variance around the time points
    time_variance = sum_of_squares.sum() / len(sum_of_squares)

    # divide by total variance
    total_variance = curr_data.var()
    timepoint_variability = time_variance / total_variance

    return timepoint_variability

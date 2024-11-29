import re
import pdb
import pandas as pd
import numpy as np
from astropy.timeseries import LombScargle
import circaPy.activity as act
import circaPy.preprocessing as prep


@prep.validate_input
def lomb_scargle_period(data, subject_no=0, low_period=20, high_period=30,
                        **kwargs):
    """
    Calculates the Lomb-Scargle periodogram for a single column in a DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        Input DataFrame with time-series data. The index represents time, and
        the columns contain observations.
    subject_no : int, optional
        The positional index of the column to analyze. Default is 0.
    low_period : float, optional
        The shortest period to search for, in hours. Default is 20.
    high_period : float, optional
        The longest period to search for, in hours. Default is 30.

    Returns
    -------
    dict
        A dictionary with the following keys:
            - "Pmax" : float
                Maximum power from the Lomb-Scargle periodogram.
            - "Period" : float
                Period corresponding to the maximum power, in hours.
            - "Power_values" : pd.Series
                Power values for all test periods, indexed by period in hours.

    Raises
    ------
    IndexError
        If `subject_no` is out of the valid range for the DataFrame columns.
    ValueError
        If `low_period` is greater than or equal to `high_period`.

    Notes
    -----
    - The function assumes evenly spaced time-series data. If the time index is
      irregular,
      the results may be inaccurate.
    - The power calculation may return NaN if the data is insufficient or
      contains only NaNs.
    """
    # Ensure the positional index is valid
    if subject_no < 0 or subject_no >= len(data.columns):
        raise IndexError(
            f"Invalid subject_no {subject_no}. Must be between 0 and"
            f"{len(data.columns) - 1}.")

    # Validate periods
    if low_period >= high_period:
        raise ValueError(f"low_period ({low_period}) must be less than"
                         f"high_period ({high_period}).")

    # get sampling frequency
    sample_freq = pd.Timedelta(pd.infer_freq(data.index)).total_seconds()

    # Define the range of frequencies to search in cycles/sample
    low_freq = 1 / (high_period * 3600)  # convert to seconds
    high_freq = 1 / (low_period * 3600)
    freq = np.linspace(low_freq, high_freq, 10000)
    freq_hours = 1 / (freq * 3600)

    # Prepare observations
    observations = data.iloc[:, subject_no].values
    if observations.size == 0 or np.all(np.isnan(observations)):
        return {"Pmax": 0,
                "Period": np.nan,
                "Power_values": pd.Series(dtype=float)}
    observation_times = np.arange(len(data)) * sample_freq

    # Calculate Lomb-Scargle periodogram
    power = LombScargle(
        observation_times,
        observations).power(
        freq,
        method='auto')

    # Handle cases where the power calculation fails
    if pd.isnull(power[0]):
        return {"Pmax": 0, "Period": 0, "Power_values": pd.Series(dtype=float)}

    # Maximum power and its corresponding period in hours
    pmax = power.max()
    best_period = freq_hours[np.argmax(power)]

    # Create a power series for the output
    power_values = pd.Series(
        power, index=freq_hours).sort_index()

    return {"Pmax": pmax, "Period": best_period, "Power_values": power_values}

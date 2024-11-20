import re
import pdb
import pandas as pd
import numpy as np
from astropy.timeseries import LombScargle
import actiPy.activity as act
import actiPy.preprocessing as prep


@prep.validate_input
def lomb_scargle_period(data, subject_no=0, low_period=20, high_period=30,
                        **kwargs):
    """
    Calculates the Lomb-Scargle periodogram for a single column in a DataFrame.

    Parameters:
        data (pd.DataFrame): Input DataFrame with time-series data.
            The index represents time, and the columns contain observations.
        subject_no (int): The positional index of the column to analyze.
            Default is 0.
        low_period (float): The shortest period to search for, in hours.
        high_period (float): The longest period to search for, in hours.

    Returns:
        dict: A dictionary with the following keys:
            - "Pmax": Maximum power from the Lomb-Scargle periodogram.
            - "Period": Period corresponding to the maximum power, in hours.
            - "Power_values": Power values for all test periods (pd.Series).
    """
    # Ensure the positional index is valid
    if subject_no < 0 or subject_no >= len(data.columns):
        raise IndexError(
            f"Invalid subject_no {subject_no}. Must be between 0 and"
            f"{len(data.columns) - 1}.")

    # get sampling frequency 
    sample_freq = pd.Timedelta(pd.infer_freq(data.index)).total_seconds()

    # Define the range of frequencies to search in cycles/sample
    low_freq = 1 / (high_period * 3600) # convert to seconds 
    high_freq = 1 / (low_period * 3600)
    freq = np.linspace(low_freq, high_freq, 10000)
    freq_hours = 1/ (freq * 3600)

    # Observation times and values
    observation_times = np.arange(len(data)) * sample_freq 
    observations = data.iloc[:, subject_no].values
    
    # Calculate Lomb-Scargle periodogram
    power = LombScargle(
        observation_times,
        observations).power(
        freq,
        method='auto')

    # Handle cases where the power calculation fails
    if pd.isnull(power[0]):
        return {"Pmax": 0, "Period": 0, "Power_values": pd.Series()}

    # Maximum power and its corresponding period in hours 
    pmax = power.max()
    best_period = freq_hours[np.argmax(power)]

    # Create a power series for the output
    power_values = pd.Series(
            power, index=freq_hours).sort_index()

    return {"Pmax": pmax, "Period": best_period, "Power_values": power_values}

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from astropy.stats import LombScargle
import pathlib
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                    "07_python_package/actiPy")
import actiPy.preprocessing as prep
from actiPy.preprocessing import _drop_level_decorator
import actiPy.waveform as wave



@_drop_level_decorator
def _period_df(data,
               animal_no: int=0,
               low_time: str="20H",
               high_time: str="30H",
               base_time: str="10S",
               base_unit: str="s"):
    """
    Applies Lombscargle periodogram for given data
    :param data:
    :param low_time:
    :param high_time:
    :param base_time:
    :return:
    """
    
    # create x and y values of observations
    time = np.linspace(0, len(data), len(data))
    y = data.iloc[:, animal_no]
    
    # convert all times into the same units (seconds)
    base_secs = pd.Timedelta(base_time).total_seconds()
    low_secs = pd.Timedelta(low_time).total_seconds()
    high_secs = pd.Timedelta(high_time).total_seconds()

    # frequency is number of 1/ cycles per base = base / cycles
    low_freq = base_secs / low_secs
    high_freq = base_secs / high_secs
    frequency = np.linspace(high_freq, low_freq, 1000)

    # find the LombScargle power at each frequency point
    power = LombScargle(time, y).power(frequency)

    # create index of timedeltas for dataframe
    index = pd.to_timedelta((1/frequency), unit=base_unit) * base_secs

    # create df out of the power values
    power_df = pd.DataFrame(power, index=index)
    
    return power_df


def idxmax_level(data,
                 level_drop: int=0):
    """
    Drops the given level and returns idx max
    :param data:
    :param level_drop:
    :return:
    """
    data.index = data.index.droplevel(level_drop)
    max_values = data.idxmax()
    
    return max_values


def get_period(data):
    """
    Function to apply lombscargle periodogram then get the internal period
    for each animal
    :param data:
    :return:
    """
    grouped_dict = {}
    for animal, label in enumerate(data.columns[:-1]):
        grouped_periods = data.groupby(level=0).apply(_period_df,
                                                    animal_no=animal,
                                                    reset_level=False)
        grouped_dict[label] = grouped_periods
        
    power_df = pd.concat(grouped_dict, axis=1)
    
    periods = idxmax_level(power_df, level_drop=0)
    
    periods.index = periods.index.droplevel(1)
    
    return periods
    

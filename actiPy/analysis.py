# script for analysis of activity data

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import actiPy.preprocessing as prep
from actiPy.plots import show_savefig_decorator, \
multiple_plot_kwarg_decorator, set_title_decorator

# function for mean waveform
def mean_activity(data,
                  period="24H",
                  *args,
                  **kwargs):
    """
    Function to return average daily activity given a certain period
    :param data:
    :param period:
    :param args:
    :param kwargs:
    :return:
    """
    
    # use split function to split into columns
    # get the mean and sem of the df
    # save as a new df
    split_data_list = prep.split_entire_dataframe(data,
                                                  period)
    mean_df_list = []
    for df in split_data_list:
        mean_df = create_mean_df(df)
        mean_df_list.append(mean_df)
    return mean_df_list
        
def create_mean_df(data):
    """
    Simple function to create new df out of mean and sem of input data
    :param data:
    :return:
    """
    mean = data.mean(axis=1)
    sem = data.sem(axis=1)
    mean_df = pd.DataFrame({"mean":mean,
                            "sem":sem},
                           index=data.index)
    mean_df.name = data.name
    return mean_df


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
    longform_df.rename(columns={0:data.name}, inplace=True)
    
    # pointplot
    _point_plot(longform_df,
                groups='group',
                ylevel=data.name,
                **kwargs)
    

def _longform_data(data, **kwargs):
    
    plotting_data = data.iloc[:,:-1].stack().reset_index()
    
    return plotting_data


@set_title_decorator
@show_savefig_decorator
@multiple_plot_kwarg_decorator
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


# TODO test for count per day
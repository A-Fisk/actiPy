# Script to define functions for analysing sleep

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pathlib
from actigraphy_analysis.preprocessing import remove_object_col, read_file_to_df

def sleep_process(data, window=4):
    """
    Function to score the PIR based activity data as sleep

    :param data: pandas dataframe to be sleep scored
    :param window: length of window, default =4 which is 40 seconds
    :return: dataframe of sleep
    """
    # if >40 seconds (4 rows) of inactivity score as 1

    rolling_sum_data = data.rolling(window).sum()

    scored_data = rolling_sum_data == 0

    return scored_data.astype(int)

# Function to take input file name and save sleep_df in the same directory
def sleep_create_df(data):
    """
    Function to take dataframe as input, remove object columns, sleep process the rest, then reattach the object
    columns, returns final df

    :param data
    """

    # remove object columns and save them
    # perform the sleep_processing
    # add object columns back in
    # return df

    # remove object columns

    df_1, columns = remove_object_col(data, return_cols=True)

    # sleep process the data

    sleep_df = sleep_process(df_1)

    # add object columns back in

    for col in columns:

        sleep_df[col.name] = col

    # return df

    return sleep_df

# Function to get hourly sum of sleep data
def create_hourly_sum(data, index_col=-1):
    """
    function that takes in a datetimeindex indexed pandas dataframe of PIR sleep scored data
    Returns as resampled into hourly bins, including the labels

    :param data:
    :param index_col:
    :return:
    """

    # resample the data with sum method
    # resample the index column with the first method
    # add index col back into the summed df
    # return the df

    df_hourly_sum = data.resample("H").sum()

    df_start = data.resample("H").first()

    # grab the column name from the original dataframe to put in the hourly sum

    col_name = data.iloc[:, index_col].name

    df_hourly_sum[col_name] = df_start.iloc[:, index_col]

    return df_hourly_sum

# Function to plot data and save to file
def simple_plot(data, save_path, dpi=300, savefig=False, showfig=True):
    """
    Function take in pandas dataframe, plot it as subplots, and then save to specified place
    :param data:
    :param destination_dir:
    :param file_name:
    :return:
    """

    # plot the file

    no_rows = len(data.columns)

    fig, ax = plt.subplots(nrows=no_rows, sharey=True)

    for axis, col in zip(ax, data.columns):

        axis.plot(data[col])

    if showfig:

        plt.show()

    if savefig:

        plt.savefig(save_path, dpi=dpi)

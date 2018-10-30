# Scripts for finding episodes
# can be sleep or activity episodes!

import pandas as pd
import matplotlib.pyplot as plt

# function to create episode dataframe
# starting off by working on just a single
# column.
# take in dataframe and column number as args
# and then return a series <- later problem
# to loop over and do for everything in the
# df

def episode_finder(data):
    """
    Function to find the episodes in the
    series - defined as from 0 to another
    0 point, must have non-0 between the two zero
    values
    Saves all in the value of total_seconds
    :param data:
    :param animal_number:
    :return:
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
    extended_time_unit = (basic_time_unit +
                          pd.Timedelta("2S")).total_seconds()
    episode_lengths_filtered = episode_series[
                                episode_series > extended_time_unit
                                ]
    # label it with the correct name
    name = data.name
    episode_lengths_filtered.name = name
    return episode_lengths_filtered
   
def episode_find_df(data,
                    LDR=-1):
    """
    finds episodes for the entire dataframe given
    by looping over each and saving them to a new
    dataframe
    :param data:
    :return:
    """
    # loop through each column
    # and find the episodes in that column
    ldr_data = data.iloc[:,LDR].copy()
    ldr_label = data.columns[LDR]
    episode_series_list = []
    for col in data:
        data_series = data.loc[:,col]
        col_episodes = episode_finder(data_series)
        episode_series_list.append(col_episodes)
    episode_df = pd.concat(episode_series_list, axis=1)
    episode_df[ldr_label] = ldr_data
    return episode_df


### Functions to plot histogram of data
def episode_histogram(data,
                      LDR=-1,
                      *args,
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
    
    ldr_label = data.columns[LDR]
    ldr_col = data.pop(ldr_label)
    data.dropna(inplace=True)
    no_animals = len(data.columns)
    fig, ax = plt.subplots(nrows=1,
                           ncols=no_animals)
    for axis, col in zip(ax, data.columns):
        axis.hist(data.loc[:,col])
        axis.set_yscale('log')
    
    if "figsize" in kwargs:
       fig.set_size_inches(kwargs["figsize"])
    # set kwarg values for showfig and savefig
    if "showfig" in kwargs and kwargs["showfig"]:
        plt.show()
    if "savefig" in kwargs and kwargs["savefig"]:
        plt.savefig(fname=kwargs['fname'])
        plt.close()


# Scripts for finding episodes
# can be sleep or activity episodes!

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import actigraphy_analysis.preprocessing as prep

# function to create episode dataframe
# starting off by working on just a single
# column.
# take in dataframe and column number as args
# and then return a series <- later problem
# to loop over and do for everything in the
# df

def episode_finder(data, *args, **kwargs):
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
    extended_time_unit = ((2*basic_time_unit) -
                          pd.Timedelta("1S")).total_seconds()
    if "min_length" in kwargs:
        extended_time_unit = pd.Timedelta(kwargs["min_length"]).total_seconds()
    episode_lengths_filtered = episode_series[
                                episode_series > extended_time_unit
                                ]
    # label it with the correct name
    name = data.name
    episode_lengths_filtered.name = name
    return episode_lengths_filtered
   
def episode_find_df(data,
                    LDR=-1,
                    *args,
                    **kwargs):
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
        col_episodes = episode_finder(data_series, *args, **kwargs)
        episode_series_list.append(col_episodes)
    episode_df = pd.concat(episode_series_list, axis=1)
    episode_df[ldr_label] = ldr_data
    check_episode_max(episode_df)
    return episode_df

def create_episode_df(data,
                      LDR=-1,
                      *args,
                      **kwargs):
    """
    Function to create entire dataframe with correct LDR and
    label columns
    :param data:
    :param LDR:
    :param args:
    :param kwargs:
    :return:
    """
    # remove object column, find episodes, reappend and return
    mod_data, object_col = prep.remove_object_col(data,
                                                  return_cols=True)
    episode_df = episode_find_df(mod_data,
                                 LDR=LDR,
                                 *args,
                                 **kwargs)
    col_name = object_col[0].name
    episode_df[col_name] = object_col[0]
    return episode_df

def check_episode_max(data,
                      max_time="6H",
                      LDR=-1):
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
    if any(max_values>comparison):
        raise ValueError("Max episode longer than %s" % max_time)
    
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
    # preprocess to be able to plot easily
    ldr_label = data.columns[LDR]
    ldr_col = data.pop(ldr_label)
    data.dropna(inplace=True)
    no_animals = len(data.columns)
    data = convert_data_to_unit(data)
    
    # Plot the data
    fig, ax = plt.subplots(nrows=1,
                           ncols=no_animals,
                           sharex=True,
                           sharey=True)
    for axis, col in zip(ax, data.columns):
        axis.hist(data.loc[:,col])
        axis.set_yscale('log')
        axis.set_title(col)
    
    # set the labelling parameters
    fig.text(0.5,
             0.01,
             'Episode duration (minutes)',
             ha='center',
             va='center')
    fig.text(0.06,
             0.5,
             "Count",
             ha="center",
             va='center',
             rotation='vertical')
    if "title" in kwargs:
        fig.suptitle(kwargs["title"])
        
    # set the extra parameters
    if "figsize" in kwargs:
       fig.set_size_inches(kwargs["figsize"])
    # set kwarg values for showfig and savefig
    if "showfig" in kwargs and kwargs["showfig"]:
        plt.show()
    if "savefig" in kwargs and kwargs["savefig"]:
        plt.savefig(fname=kwargs['fname'])
        plt.close()

# unfortunately have to basically copy paste a lot because
# can't figure out how to modify axis objects
# once already created to plot each df separately
def episode_histogram_all_conditions(data_list,
                                     LDR=-1,
                                     *args,
                                     **kwargs):
    """
    Function to plot all the different conditions in the list
    as their own row in a histogram plot
    :param data:
    :param LDR:
    :param args:
    :param kwargs:
        bins: if given will take bins in seconds and convert to
            seconds. Assumes input as an array of data,
            takes the second last value and assigns ta
    :return:
    """

    # preprocess to be able to plot easily
    tidied_data_list = []
    label_list = []
    for df in data_list:
        df = prep.remove_object_col(df)
        ldr_label = df.columns[LDR]
        ldr_col = df.pop(ldr_label)
        data = df#convert_data_to_unit(df)
        tidied_data_list.append(data)
        label_list.append(df.name)
    no_animals = len(tidied_data_list[0].columns)

    # let the function define bins as needed
    if "bins" in kwargs:
        bins = kwargs["bins"]
    else:
        bins = 10
    if "logy" in kwargs:
        log = kwargs["logy"]
    else:
        log = False
    
    # Plot the data
    fig, ax = plt.subplots(nrows=len(data_list),
                           ncols=no_animals,
                           sharex=True,
                           sharey=True)
    for row, condition in enumerate(label_list):
        plotting_df = tidied_data_list[row]
        for col_plot, col_label in enumerate(plotting_df):
            plotting_col = plotting_df.loc[:,col_label].dropna()
            curr_axis = ax[row,col_plot]
            curr_axis.hist(plotting_col,
                           bins=bins,
                           log=log,
                           density=True)
            # curr_axis.set(xlim=[0,bins[-2]])
            if row == 0:
                curr_axis.set_title(col_label)
            if col_plot == 0:
                curr_axis.set_ylabel(label_list[row])
    fig.subplots_adjust(hspace=0,
                        wspace=0)
    
    # set the labelling parameters
    if "xtitle" in kwargs:
        xtitle = kwargs["xtitle"]
    else:
        xtitle = "Episode duration"
    fig.text(0.5,
             0.01,
             xtitle,
             ha='center',
             va='center')
    fig.text(0.03,
             0.5,
             "Normalised density",
             ha="center",
             va='center',
             rotation='vertical')
    if "title" in kwargs:
        fig.suptitle(kwargs["title"])
        
    # set the extra parameters
    if "figsize" in kwargs:
        fig.set_size_inches(kwargs["figsize"])
    # set extra kwarg parameters
    if "showfig" in kwargs and kwargs["showfig"]:
        plt.show()
    if "savefig" in kwargs and kwargs["savefig"]:
        plt.savefig(fname=kwargs['fname'])
        plt.close()

def ep_hist_conditions_from_df(data,
                               LDR=-1,
                               *args,
                               **kwargs):
    """
    Function to take in dataframe, separate into list of conditions
    then plot
    :param data:
    :param LDR:
    :param args:
    :param kwargs:
    :return:
    """
    data_list = prep.separate_by_condition(data)
    if "fname" in kwargs:
        kwargs["title"] = kwargs["fname"].stem
    episode_histogram_all_conditions(data_list=data_list,
                                     LDR=LDR,
                                     *args,
                                     **kwargs)

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

# script for analysis of activity data

import pandas as pd
import numpy as np
import actigraphy_analysis.preprocessing as prep

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

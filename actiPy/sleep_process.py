# functions for sleep processing

import os
import numpy as np
import actiPy.preprocessing as prep


def sleep_process(data, window=4):
    """
    Function to score activity data as sleep given
    a certain window of activity
    Future development implement thresholds for breaking
    sleep episodes.
    Returns scored dataframe
    :param data:
    :param window:
    :return:
    """
    # score > window as inactivity score of 1
    rolling_sum_data = data.rolling(window).sum()
    bool_scored_data = rolling_sum_data == 0
    scored_data = bool_scored_data.astype(int)
    return scored_data


def create_scored_df(data, **kwargs):
    """
    Function to take dataframe as input and return the same data
    and labels but scored for sleep -> then appropriate to save
    :param data:
    :return:
    """
    # remove object columns, score, return columns to df
    sleep_df = _score_active_times(data, **kwargs)
    return sleep_df


def _score_active_times(data,
                        ldr_col=-1,
                        test_col=0,
                        threshold=1,
                        drop_level=True):
    """
    Scores all times between start and end of activity as sleep, sets all
    other values to 0
    :param data:
    :param ldr_col:
    :param test_col:
    :param threshold:
    :param drop_level:
    :return:
    """
    if drop_level:
        data = data.reset_index(0)
        label_name = data.columns[0]
        label_col = data.pop(label_name)

    # score the df minus the LDR
    ldr_label = data.columns[ldr_col]
    ldr_data = data.pop(ldr_label)
    scored_df = sleep_process(data)

    # find start and end of activity
    mask = data.iloc[:, test_col] > threshold
    start = data.where(mask).first_valid_index()
    end = data.where(mask)[::-1].first_valid_index()

    # set scored df times outside of start and end to be 0
    scored_df.loc[:start] = 0
    scored_df.loc[end:] = 0
    scored_df[ldr_label] = ldr_data

    if drop_level:
        scored_df[label_name] = label_col
        new_cols = [scored_df.columns[-1], scored_df.index]
        scored_df.set_index(new_cols, inplace=True)

    return scored_df


def alter_file_name(file_name,
                    suffix,
                    remove_slice_after=-9):
    """
    Function to take in the file name and remove part of the
    name, replace with "suffix" and rename the file
    :param file_name:
    :param suffix:
    :param slice_range:
    :return:
    """
    new_file_name = file_name.stem[:remove_slice_after] + \
        suffix + \
        file_name.suffix
    new_file_path = file_name.parent / new_file_name
    os.rename(file_name, new_file_path)

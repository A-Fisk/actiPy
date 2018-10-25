# functions for sleep processing

import actigraphy_analysis.preprocessing as prep

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
    bool_scored_data = rolling_sum_data==0
    scored_data = bool_scored_data.astype(int)
    return scored_data

def create_scored_df(data):
    """
    Function to take dataframe as input and return the same data
    and labels but scored for sleep -> then appropriate to save
    :param data:
    :return:
    """
    # remove object columns, score, return columns to df
    df_1, columns = prep.remove_object_col(data, return_cols=True)
    sleep_df = sleep_process(df_1)
    for col in columns:
        sleep_df[col.name] = col
    return sleep_df
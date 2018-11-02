# functions for sleep processing

import numpy as np
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
    sleep_df = scored_active_times(df_1)
    for col in columns:
        sleep_df[col.name] = col
    return sleep_df

def scored_active_times(data,
                        window=4,
                        LDR=-1,
                        threshold=9,
                        *args,
                        **kwargs):
    """
    Function to only sleep process between sections that have activity
    in them
    :param data:
    :param window:
    :param args:
    :param kwargs:
    :return:
    """
    
    # find the start and end of any activity and then only score betweween
    # those times
    # find first non-0 time
    data_use = data.copy()
    ldr = data_use.pop(data_use.columns[LDR])
    data_nan = data_use.replace(0, np.nan).copy()
    
    # find the first time that consistently > 0 to filter out noise
    resampled = data_use.resample('30T').mean()
    threshold_df = resampled[resampled>threshold]
    start_resampled = threshold_df.first_valid_index()
    string_start = str(start_resampled)
    data_from_start_activity = data_nan[string_start:]
    
    # find the last time that is consistently >0
    end_resampled = threshold_df.iloc[::-1].first_valid_index()
    string_end = str(end_resampled)
    data_to_end_activity = data_nan[:string_end]
    
    # Now find the non - 0 times
    first_time = data_from_start_activity.first_valid_index()
    last_time = data_to_end_activity[::-1].first_valid_index()

    # only score period between active times
    data_to_score = data_use.loc[first_time:last_time].copy()
    scored_data = sleep_process(data_to_score, window)
    
    # put scored values back into the dataframe
    data_final = data_use.copy()
    data_final.loc[:first_time] = 0
    data_final.loc[last_time:] = 0
    data_final.loc[first_time:last_time] = scored_data
    data_final.iloc[:,LDR] = ldr
    
    return data_final
    
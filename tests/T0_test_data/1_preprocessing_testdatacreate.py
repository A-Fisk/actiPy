# import modules that will be used

import numpy as np
import pandas as pd

# Script to create data that can be used for 1_test_preprocessing.

def create_remove_object_col_data():
    """
    Function to create a csv file which can be read into a dataframe which contains a float column and an object column
    :return: creates csv file in current directory
    """

    # Create lists with correct types of data
    # turn into a Dataframe
    # save dataframe to a csv file in current directory

    np.random.seed(42)

    # first list contains only floats

    col_1_list = np.random.rand(100)

    col_2_list = np.random.randint(0, 1, size=100, dtype=int)

    col_3_list = np.random.randint(0, 1, size=100, dtype=int).astype("O")

    col_4_list = np.random.randint(10, 20, size=100, dtype=int).astype("O")

    list_of_columns = [col_1_list,
                       col_2_list,
                       col_3_list,
                       col_4_list]

    # Turn these lists into a dataframe

    test_data_df = pd.DataFrame(list_of_columns).T

    # save as a csv in current directory

    test_data_df.to_csv('1_remove_object_col_testdata.csv')

# run function to create remove object col test data

create_remove_object_col_data()


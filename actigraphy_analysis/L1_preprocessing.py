import pandas as pd


# This script contains functions which are useful for preprocessing of PIR data

# function to remove column if object

def remove_object_col(data, return_cols=False):
    """
    Function to check the data type in each column
    and drop it if it is an object
    Does not distinguish between float, int, strings
    :param data: pandas dataframe to check
    :param return_cols: Boolean - default False, returns columns as a list
    :return: pandas dataframe without object columns
    :return: if return_cols is true, returns list of dropped columns
    """

    # Check each column type
    # drop the columns that are objects
    # return the dataframe

    dropped_cols = []
    for column in data.columns:
        column_data = data.loc[:, column]
        if column_data.dtype == 'O':
            current_col = data.loc[:, column]
            dropped_cols.append(current_col)
            data = data.drop(column, axis=1)

    if return_cols:
        return data, dropped_cols

    else:
        return data


# Function to split dataframe into periods based on label_column
def separate_by_condition(data, label_col=-1):
    """
    Function to separate activity data based upon the condition
    defined by a label column. e.g. separate into "Baseline",
    "Disrupted", "Post_Baseline"
    :param data: Dataframe to split, requires label column
    :param label_col: int, which column to select based upon, default -1
    :return: list of dataframes, length of list determined by
        number of unique labels
    """

    # select the unique values in the label column
    # slice the data based upon the label column values
    # append to list and return list of separated dataframes

    unique_conditions = data.iloc[:, label_col].unique()
    list_of_dataframes_by_condition = []
    for condition in unique_conditions:
        temporary_sliced_data = data[data.iloc[:, label_col] == condition]
        list_of_dataframes_by_condition.append(temporary_sliced_data)

    return list_of_dataframes_by_condition

# Function to read files in as a pandas dataframe in standard way
def read_file_to_df(file_name):
    """
    function to take given csv file name and turn it into a df
    :param file_name:
    :return:
    """

    # quick error handling to see if is a csv file
    if file_name.suffix != ".csv":
        raise ValueError("Not a csv file")
    df = pd.read_csv(file_name,
                     index_col=0,
                     parse_dates=True)
    return df


# Function to check subdirectory and create if doesn't exist
def create_subdir(input_directory, subdir_name):
    """
    Function takes in Path object of input_directory
    and string of subdir name, adds them together, checks if it
    exists and if it doesn't creates new directory

    :param input_directory:
    :param subdir_name:
    :return:
    """

    # create path name
    # check if exists
    # create it if it doesn't exist
    # return path name

    sub_dir_path = input_directory / subdir_name
    if not sub_dir_path.exists():
        sub_dir_path.mkdir()
    return sub_dir_path


# Function to create file_name_path
def create_file_name_path(directory, file, save_suffix):
    """
    Simple function to put together directory, file.stem,
    and suffix to create path
    :param directory:
    :param file:
    :param save_suffix:
    :return:
    """

    # combine directory, file stem and save suffix
    file_path = directory / (file.stem + save_suffix)
    return file_path

# Create save_pipeline class with objects
# for saving csv and plots depending on the method used
class SaveObjectPipeline:
    """
    Class object for saving data to a file.
    Main object used for processing data and saving it to a directory
    Separate methods for saving dataframes to csv files
    and for creating
    and saving plots to a file

    init method globs all the files in the input_directory
    and creates a df_list with dataframes of all the files in
    the input_directory

    Takes the arguments initially of
    Input_directory - place to search for files to process
    Subdir_name - name for subdirectory to be created
        in input_directory to hold new files
    search_suffix - default .csv, name to glob for files in input_directory

    """

    # init method to create attributes
    def __init__(self, input_directory, search_suffix=".csv"):

        self.processed_list = []
        self.input_directory = input_directory
        self.search_suffix = search_suffix

        # create the file list by globbing for the search suffix
        self.file_list = list(self.input_directory.glob("*" +
                                                        self.search_suffix))

        # read all the dfs into a list
        self.df_list = []

        for file in self.file_list:
            temp_df = read_file_to_df(file)
            self.df_list.append(temp_df)

    # method for saving a csv file
    def save_csv_file(self, function_name, subdir_name, save_suffix):
        """
        Method that applies a defined function to all the
        dataframes in the df_list and saves them to the subdir that
        is also created

        :param function_name:
        :param save_suffix:
        :param subdir_name
        :return:
        """

        # create the subdirectory
        # For every df in the list
        # apply the function
        # create the name to save it
        # save the df there
        # Save to a processed list so can use for plotting

        subdir_path = create_subdir(self.input_directory,
                                    subdir_name=subdir_name)

        for df, file in zip(self.df_list, self.file_list):
            temp_df = function_name(df)
            file_name_path = create_file_name_path(subdir_path,
                                                   file,
                                                   save_suffix)
            temp_df.to_csv(file_name_path)
            self.processed_list.append(temp_df)

    # method for saving a plot
    def create_plot(self,
                    function_name,
                    subdir_name,
                    data_list=None,
                    save_suffix='.png',
                    showfig=False,
                    savefig=True,
                    dpi=300):
        """
        Method to take each df and apply given plot function and save to file
        Default parameters of showfig = False
        and savefig = True but can be changed

        :type save_suffix: str
        :param save_suffix:
        :param dpi:
        :param function_name:
        :param showfig:
        :param savefig:
        :return:
        """

        # create subdir
        # for every df in the list
        # create the save name
        # remove the object col
        # apply the plotting function, passing savefig and showfig arguments to the function and the path to save name

        # define the data list
        if data_list is None:
            data_list = self.processed_list

        # create the subdir
        subdir_path = create_subdir(self.input_directory,
                                    subdir_name=subdir_name)

        # loop through the dfs and pass to plotting function (saves by default))
        for df, file in zip(data_list, self.file_list):
            file_name_path = create_file_name_path(subdir_path,
                                                   file, save_suffix)
            temp_df = remove_object_col(df, return_cols=False)
            function_name(temp_df,
                          file_name_path,
                          showfig=showfig,
                          savefig=savefig,
                          dpi=dpi)
        
        # TODO update to save as svg format by default.

######### Group of functions for split by period function ##########

def create_period_index(data, period=None):
    """
    Function to create a list of timestamps
    that vary by the given period
    which can then be used to slice a dataframe by
    :param data: timestamp indexed data
        so can grab the start and end for the period range
    :param period: in "%H %T" format
        defaults to 24H 0T if not given
    :return: list of timestamps a given period apart
    """

    # set the default value for period if not given

    if not period:
        period = "24H 0T"

    # grab the start and the end of the data
    # index and use this to create the range
    start, end = data.index[0], data.index[-1]

    # create period range using these parameters
    period_index_list = pd.date_range(start=start,
                                      end=end,
                                      freq=period)

    return period_index_list

def slice_dataframe_by_index(data_series, index_list):
    """
    Function that takes a timestamp indexed
    series and slices according to the indexes
    provided in the index list
    Returns a dataframe of generically indexed values
    with each period in a separate column
    :param data_series: datetimeindex series
    :param index_list: output of create_period_index expected,
        list of datetimes to slice by
    :return: generically indexed dataframe with each period in
        a separate column
    """

    # loop through each day and append the values to a list
    data_by_day_list = []
    for day_start, day_end in zip(index_list[:-1], index_list[1:]):
        day_data = data_series.loc[day_start:day_end].values
        data_by_day_list.append(day_data)

    # append the final day of data as well
    final_day_start = index_list[-1]
    final_day_data = data_series.loc[final_day_start:].values
    data_by_day_list.append(final_day_data)

    # concat into one large dataframe
    period_sliced_dataframe = pd.DataFrame(data_by_day_list).T

    return period_sliced_dataframe

def create_ct_based_index(period_sliced_data, CT_period=None):
    """
    Create new index for data based on a given length of circadian time
    given want the dataframe to be indexed to be
    equivalent to 24 hours, needs to be reindexed
    at a frequency of seconds and miliseconds to
    get required accuracy
    :param period_sliced_data: data sliced by period with generic index
        used to get length of new bins
    :param CT_period: defaults to "24H 0T" can change if required
    :return: datetimeindex
    """

    # set the default CT value
    if not CT_period:
        CT_period = "24H 0M"

    # create new index frequency from how close the
    # old dataframe is in seconds to 24 hours
    CT_seconds = pd.Timedelta(CT_period).total_seconds()
    dataframe_seconds = len(period_sliced_data)
    ratio_seconds = CT_seconds/dataframe_seconds
    int_seconds = int(ratio_seconds)
    miliseconds = round((ratio_seconds - int_seconds)*1000)
    new_frequency = str(int_seconds) + "S " + str(miliseconds) + "ms"

    # create new index from frequency and length of dataframe
    new_index = pd.timedelta_range(start="0S",
                                   freq=new_frequency,
                                   periods=dataframe_seconds)

    return new_index

def split_dataframe_by_period(data,
                              animal_number,
                              period=None,
                              CT_period=None):
    """
    Function to split a long dataframe into
    each day given by period as a different column
    indexed by *circadian* time
    :param data: datetimeindexed dataframe
    :param animal_number: which column to slice
    :param period: default 24H, period to slice by
    :param CT_period: default 24H, circadian period to index final 
        dataframe by
    :return: CT period datetime indexed dataframe   
        with each day in a subsequent column
    """

    # create index of days to slice by
    period_based_index = create_period_index(data, period)

    # select just the animal we want and slice that
    animal_data_series = data.iloc[:, animal_number]
    period_sliced_data = slice_dataframe_by_index(animal_data_series,
                                                  period_based_index)

    # create the new index and re-index the data
    new_index = create_ct_based_index(period_sliced_data, CT_period)
    period_sliced_data.index = new_index

    # tidy up columns to equal day numbers
    # and name to equal animal name
    number_of_days = len(period_sliced_data.columns)
    period_sliced_data.columns = range(number_of_days)
    animal_label = data.columns[animal_number]
    period_sliced_data.name = animal_label

    return period_sliced_data

from functools import wraps
import pingouin as pg
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
idx = pd.IndexSlice
# This script contains functions which are useful for preprocessing of
# actigraphy data

###### Decorators first #####


def plot_kwarg_decorator(func):
    """
    Universal decorator for plot formatting and configuration.
    Handles xlabels, ylabels, titles, legends, time formatting, saving, and showing plots.
    :param func: The plotting function to decorate.
    :return: A decorated function that applies plot configurations.
    """
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        # Call the original plotting function
        fig, ax, params_dict = func(data, *args, **kwargs)

        final_ax = ax[-1]
        # Configure x-axis time formatting
        if "timeaxis" in params_dict and params_dict["timeaxis"]:
            xfmt = kwargs.get("xfmt", mdates.DateFormatter("%H:%M"))
            final_ax.xaxis.set_major_formatter(xfmt)
            interval = kwargs.get("interval", params_dict.get("interval", 1))
            final_ax.xaxis.set_major_locator(
                mdates.HourLocator(interval=interval))
            fig.autofmt_xdate()

        # Set x-axis label
        xlabel = kwargs.get("xlabel", params_dict.get("xlabel", ""))
        xlabelpos = kwargs.get("xlabelpos", (0.5, 0.05))
        if xlabel:
            fig.text(
                xlabelpos[0],
                xlabelpos[1],
                xlabel,
                ha="center",
                va="center")

        # Set y-axis label
        ylabel = kwargs.get("ylabel", params_dict.get("ylabel", ""))
        ylabelpos = kwargs.get("ylabelpos", (0.02, 0.5))
        if ylabel:
            fig.text(
                ylabelpos[0],
                ylabelpos[1],
                ylabel,
                ha="center",
                va="center",
                rotation="vertical"
            )

        # Set plot title
        title = kwargs.get("title", params_dict.get("title", ""))
        if title:
            fig.suptitle(title)

        # Configure legend
        if kwargs.get("legend", False):
            legend_loc = kwargs.get("legend_loc", 1)
            handles, labels = final_ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc=legend_loc)

        # Configure x-axis limits
        if "xlim" in kwargs or "xlim" in params_dict:
            xlim = kwargs.get("xlim", params_dict.get("xlim", None))
            if xlim:
                final_ax.set_xlim(xlim)

        # Configure figure size
        if "figsize" in kwargs:
            fig.set_size_inches(kwargs["figsize"])

        # Save or show the plot
        if kwargs.get("savefig", False):
            fname = kwargs.get("fname", "plot.png")
            plt.savefig(fname)
            plt.close()
        if kwargs.get("showfig", False):
            plt.show()

        return fig, ax, params_dict

    return wrapper


def validate_non_zero(func):
    """
    Decorator to check if any of the DataFrames or Series passed to the function
    consist only of zeros. Raises a ValueError if any consist only of zeros.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check all positional arguments
        for arg in args:
            if isinstance(
                    arg, (pd.DataFrame, pd.Series)) and (
                    arg.values == 0).all():
                raise ValueError(f"Input {arg} consists only of zeros.")

        # Check all keyword arguments
        for key, value in kwargs.items():
            if isinstance(
                    value, (pd.DataFrame, pd.Series)) and (
                    value.values == 0).all():
                raise ValueError(f"Input {key} consists only of zeros.")

        # Call the original function
        return func(*args, **kwargs)

    return wrapper


def _drop_level_decorator(func):
    """
    removes top level before passing to function and re-indexes before returning
    :param func:
    :return:
    """
    def wrapper(data, drop_level=True, reset_level=True, **kwargs):

        # drop top level of axis if asked, save
        if drop_level:
            data_dropped = data.reset_index(0)
            label_name = data_dropped.columns[0]
            label_col = data_dropped.pop(label_name)
        else:
            data_dropped = data.copy()

        # call the function on the data
        new_data = func(data_dropped, **kwargs)

        # re-index to original level
        if reset_level and drop_level:
            new_data[label_name] = label_col
            new_cols = [new_data.columns[-1], new_data.index]
            new_data.set_index(new_cols, inplace=True)

        return new_data

    return wrapper


def _name_decorator(func):
    """
    Copies metadata if present
    :param func:
    :return:
    """
    def wrapper(data, **kwargs):

        # call original function
        new_data = func(data, **kwargs)

        # append metadata if there
        if hasattr(data, "name"):
            new_data.name = data.name

        return new_data

    return wrapper


def _remove_lights_decorator(func):
    """
    Removes light and reappends after called
    """
    def wrapper(data, ldr_col=-1, **kwargs):

        # remove ldr
        ldr_label = data.columns[ldr_col]
        ldr_data = data.pop(ldr_label)

        # call function
        new_data = func(data, **kwargs)

        # reappend ldr
        new_data[ldr_label] = ldr_data

        return new_data

    return wrapper


def sep_by_index_decorator(func):
    """
    Separates into a list of dataframes by the given level of the index and
    passes to the function
    """

    def wrapper(data, level=0, **kwargs):

        vals = data.index.get_level_values(level).unique()
        for val in vals:
            temp_df = data.loc[idx[val, :], :]
            temp_df.reset_index(0, drop=True, inplace=True)
            temp_df.name = val
            list_by_vals.append(temp_df)

        func(list_by_vals, **kwargs)

    return wrapper


def _groupby_decorator(func):
    """
    Returns grouped values for func
    :param func:
    :return:
    """
    def wrapper(data, group=True, level=0, **kwargs):

        if group:
            new_data = data.groupby(level=level).apply(func)

        else:
            new_data = func(data)

        return new_data

    return wrapper


# assertion for split by dataframe to catch errors of removing too many levels


def assert_index_datetime(f):
    @wraps(f)
    def wrapper(df, *args, **kwargs):
        assert df.index.dtype == pd.to_datetime(['2013']).dtype, \
            "Not a datetime index, check drop_levels"
        return f(df, *args, **kwargs)
    return wrapper


# function to remove column if object
def remove_object_col(data, return_cols=False):
    """
    Function to check the data type in each column
    and drop it if it is an object
    does not distinguish between float, int, strings
    :param data: pandas dataframe to check
    :param return_cols: Boolean - default False, returns columns as a list
    :return: pandas dataframe without object columns
    :return: if return_cols is true, returns list of dropped columns
    """

    # Check each column type
    # drop the columns that are objects
    # return the dataframe

    dropped_cols = []
    if hasattr(data, "name"):
        name = data.name
    else:
        name = "NaN"
    for column in data.columns:
        column_data = data.loc[:, column]
        if column_data.dtype == 'O':
            current_col = data.loc[:, column]
            dropped_cols.append(current_col)
            data = data.drop(column, axis=1)
    data.name = name

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
    # remove nan values
    unique_conditions = unique_conditions[~pd.isnull(unique_conditions)]
    list_of_dataframes_by_condition = []
    for condition in unique_conditions:
        temporary_sliced_data = data[data.iloc[:, label_col] == condition]
        temporary_sliced_data.name = condition
        list_of_dataframes_by_condition.append(temporary_sliced_data)

    return list_of_dataframes_by_condition


# Function to read files in as a pandas dataframe in standard way
def read_file_to_df(file_name,
                    index_col=0,
                    header=0,
                    **kwargs):
    """
    function to take given csv file name and turn it into a df
    :param file_name:
    :return:
    """

    # quick error handling to see if is a csv file
    if file_name.suffix != ".csv":
        raise ValueError("Not a csv file")
    df = pd.read_csv(file_name,
                     index_col=index_col,
                     header=header,
                     parse_dates=True)
    name = file_name.stem
    df.name = name
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
    # define the file name
    if isinstance(file, str):
        name = file
    else:
        name = file.stem

    # combine directory, name and save suffix
    file_path = directory / (name + save_suffix)
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
    def __init__(self,
                 input_directory="",
                 save_directory="",
                 subdir_name="",
                 func=(globals(),
                       "read_file_to_df"),
                 search_suffix=".csv",
                 readfile=True,
                 **kwargs):

        # create the lists to be used later and save the arguments as
        # object attributes
        self.input_directory = input_directory
        self.search_suffix = search_suffix
        self.save_directory = save_directory
        self.subdir_name = subdir_name
        self.processed_list = []
        self.processed_file_list = []
        self.processed_df = []
        self.processed_df_filename = []

        # create the file list by globbing for the search suffix
        self.file_list = sorted(
            self.input_directory.glob("*" +
                                      self.search_suffix)
        )

        # create the subdirectory in the save dir
        self.subdir_path = create_subdir(
            self.save_directory,
            subdir_name=self.subdir_name
        )

        # read all the dfs into a list
        self.object_list = []
        if readfile:
            read_fx = getattr(func[0], func[1])
            for file in self.file_list:
                temp_df = read_fx(file,
                                  **kwargs)
                self.object_list.append(temp_df)

    # method for saving a csv file
    def process_file(self,
                     function=(),
                     save_suffix='.csv',
                     savecsv=False,
                     object_list=None,
                     file_list=None,
                     create_df=False,
                     savedfcsv=False,
                     set_name: bool = True,
                     **kwargs):
        """
        Method that applies a defined function to all the
        dataframes in the df_list and saves them to the subdir that
        is also created

        :param function_name:
        :param save_suffix:
        :param subdir_name
        :return:
        """

        # define the function to be used for processing
        func = getattr(function[0], function[-1])

        # set the default lists to iterate through
        if object_list is None:
            object_list = self.object_list
        if file_list is None:
            file_list = self.file_list

        # iterate through the objects and call the function on each one
        for object, file in zip(object_list, file_list):
            temp_df = func(object, **kwargs)
            self.processed_list.append(temp_df)
            # create the file name path and put in attribute list
            file_name_path = create_file_name_path(
                self.subdir_path,
                file,
                save_suffix
            )
            self.processed_file_list.append(file_name_path)

            # save the csv to the subdirectory if asked to do so
            if savecsv:
                temp_df.to_csv(file_name_path)

        # create a dataframe from the processed files
        if create_df:
            keys = [x.stem for x in self.processed_file_list]
            items = self.processed_list
            dictionary = dict(zip(keys, items))
            self.processed_df = pd.concat(dictionary)
            if set_name:
                self.processed_df.name = function[1]
            else:
                self.processed_df.name = items[0].columns.name

            # rename columns and axis
            self.processed_df.index.rename('group', level=0, inplace=True)
            self.processed_df.columns.name = 'animals'

            # save the csv to the function name
            if savedfcsv:
                file_name_path = create_file_name_path(
                    self.subdir_path,
                    function[1],
                    save_suffix
                )
                self.processed_df_filename = file_name_path
                self.processed_df.to_csv(file_name_path)

    # method for saving a plot

    def create_plot(self,
                    function=(),
                    save_suffix='.png',
                    data_list=None,
                    file_list=None,
                    remove_col=True,
                    subdir_path=None,
                    **kwargs):
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

        # grab the function as an attribute so can properly call
        # if called as a string does odd things
        func = getattr(function[0], function[1])

        # define the lists to iterate through
        if data_list is None:
            data_list = self.object_list
        elif "processed" in data_list:
            data_list = self.processed_list
        if file_list is None:
            file_list = self.file_list
        if subdir_path is None:
            subdir_path = self.subdir_path

        # loop through the dfs and pass to plotting function
        for df, file in zip(data_list, file_list):
            file_name_path = create_file_name_path(
                subdir_path,
                file,
                save_suffix
            )
            if remove_col:
                temp_df = remove_object_col(df, return_cols=False)
            else:
                temp_df = df.copy()
            if isinstance(temp_df, pd.DataFrame):
                temp_df.name = df.name
            func(temp_df,
                 fname=file_name_path,
                 **kwargs)


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
    ratio_seconds = CT_seconds / dataframe_seconds
    int_seconds = int(ratio_seconds)
    miliseconds = round((ratio_seconds - int_seconds) * 1000)
    new_frequency = str(int_seconds) + "S " + str(miliseconds) + "ms"

    # create new index from frequency and length of dataframe
    new_index = pd.date_range(start="2010-01-01 00:00:00",
                              freq=new_frequency,
                              periods=dataframe_seconds)

    return new_index


@_drop_level_decorator
@assert_index_datetime
def split_dataframe_by_period(data,
                              animal_number: int = 0,
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


def split_entire_dataframe(data,
                           period=None,
                           CT_period=None,
                           **kwargs):
    """
    applies split_dataframe_by_period to each animal in turn in the dataframe
    :param data: dataframe
    :param period: default none
    :param CT_period: default none.
    :param label col: not using as assuming already dropped before coming
        into this function
    :return: list of split dataframes
    """

    # apply split to each column
    # and save in a list
    # return the list
    split_df_list = []
    for num, column in enumerate(data.columns):
        temp_split_df = split_dataframe_by_period(data,
                                                  drop_level=False,
                                                  animal_number=num,
                                                  period=period,
                                                  CT_period=CT_period,
                                                  **kwargs)
        temp_split_df.name = column
        split_df_list.append(temp_split_df)
    return split_df_list


def split_all_animals(df,
                      ignore_index: bool = True,
                      drop_level=True,
                      reset_level=False,
                      **kwargs):
    # get all animals in one big df
    split_dict = {}
    for no, col in enumerate(df.columns[:-1]):
        # split by period, then plot mean +/- sem?
        split_df = split_dataframe_by_period(df,
                                             drop_level=drop_level,
                                             reset_level=reset_level,
                                             animal_number=no)
        split_dict[col] = split_df

    all_df = pd.concat(split_dict, axis=1, ignore_index=ignore_index)

    return all_df


def remap_LDR(data,
              ldr_col=-1,
              test_col=1,
              test_activ_value=10,
              test_ldr_value=100,
              max_ldr_value=150,
              invert=True,
              drop_level=True,
              **kwargs):
    """
    Function to remap LDR values from light = high to
    light = low - allows easier plotting of actigraphy data
    because colouring in the light phase is UGLY
    :param light_data:
    :return:
    """
    # remap the LDR value
    # Aim: remap all 0 values between start and end of light cycles
    # to inverse so shows up as grey on the actogram

    # remove level if multi-index and save those values for later
    if drop_level:
        data = data.reset_index(0)
        label_name = data.columns[0]
        label_col = data.pop(label_name)

    # Step one, select just the time of the activity cycles
    test_data = data.iloc[:, test_col].copy()
    mask = test_data > test_activ_value
    start = test_data.where(mask).first_valid_index()
    end = test_data.where(mask)[::-1].first_valid_index()

    light_data = data.iloc[:, ldr_col].copy()
    light_mask = light_data > test_ldr_value
    # Set the high values to all be 150
    light_data = light_data.mask(light_mask, other=max_ldr_value)

    # Step two, invert the selected data
    if invert:
        light_data = max_ldr_value - light_data

    # Step three, assign to a new dataframe and return
    new_data = data.copy()
    ldr_label = new_data.columns[ldr_col]
    new_data.loc[start:end, ldr_label] = light_data.loc[start:end]

    # return the label col and reindex
    if drop_level:
        new_data[label_name] = label_col
        new_cols = [new_data.columns[-1], new_data.index]
        new_data.set_index(new_cols, inplace=True)

    return new_data


def slice_by_label_col(data,
                       label_col=-1,
                       section_label="Disrupted",
                       baseline_length="6D",
                       post_length="15D",
                       drop_level=True,
                       **kwargs):
    """
    Function to slice the dataframe into a shorter period based on the
    label column. Primary use for defining times to use for
    creating pretty actograms
    :param data:
    :param label_col:
    :param section_label:
    :param baseline_length: how many days before disruption
        starts to slice
    :param post_length: how many days (or just time period
        generally) to slice afterwards
    :return:
    """

    name = data.name
    # if multi-index then drop top level and use that as the index
    if drop_level:
        data = data.reset_index(0)
        label_col = 0

    # select given time before and after the selected period
    start_timeshift = pd.Timedelta(baseline_length)
    end_timeshift = pd.Timedelta(post_length)
    disrupted_index = data[data.iloc[:, label_col] == section_label].index
    start = disrupted_index[0] - start_timeshift
    end = disrupted_index[-1] + end_timeshift
    data_new = data.loc[start:end].copy()

    data_new.name = name
    if drop_level:
        new_index = data_new.columns[0]
        data_new.set_index(new_index, append=True, inplace=True)
        data_new = data_new.reorder_levels([1, 0])
    return data_new


def clean_data(data,
               append_post=True,
               post_label='post_dd',
               **kwargs):
    """
    Function to clean dataframe into given time before and after the
    light period of interest, also append post_dd if asked
    :param data:
    :param post_label:
    :param kwargs:
    :return:
    """
    # Aim -> split by label col 6D baseline 15 d post baseline
    # then append post_dd
    sliced_data = slice_by_label_col(data, **kwargs)

    if append_post:
        # create post-dd in same format
        index_name = data.index.get_level_values(0).name
        post_dd = pd.concat([data.loc[post_label]],
                            keys=[post_label],
                            names=[index_name])

        # put post_dd back into the df
        final_df = pd.concat([sliced_data, post_dd])

    else:
        final_df = sliced_data

    return final_df


@_name_decorator
def _convert_to_units(data,
                      base_freq="10S",
                      target_freq="1H",
                      **kwargs):
    """
    Function to convert data from current frequency
    :param data:
    :param base_freq:
    :param target_freq:
    :return:
    """
    base_secs = pd.Timedelta(base_freq).total_seconds()
    target_secs = pd.Timedelta(target_freq).total_seconds()
    new_data = data.copy()
    new_data = (new_data * base_secs) / target_secs
    return new_data


@_name_decorator
@_groupby_decorator
def _resample(data,
              target_freq: str = "1H",
              level: int = 1,
              **kwargs):
    """
    resamples to the target frequency
    :param data:
    :param target_freq:
    :param kwargs:
    :return:
    """
    new_data = data.copy()
    new_data = new_data.resample(target_freq, level=level).mean()

    return new_data


def split_list_with_periods(name_df: pd.DataFrame,
                            df_list: list):
    """
    Function that takes in a list of dataframes and a separate dataframe with
    all the internal periods in it.
    Loops through the various levels to apply split_by_period to each
    animal/section/condition in the list (assuming list is of different
    conditions) as given by the name df
    :param name_df:
    :param df_list:
    :return:
    """
    # get values of each level we will loop through to select right period
    condition_names = name_df.index.get_level_values(0).unique()
    light_periods = name_df.index.get_level_values(1).unique()
    animal_numbers = name_df.columns

    split_dict = {}
    # loop through condition dfs
    for condition_number, condition_name in enumerate(condition_names):
        df = df_list[condition_number]
        condition_dict = {}

        # loop through light periods
        for section in light_periods:
            section_data = df.loc[section]
            section_dict = {}

            # need to loop through animal numbers
            for animal_no, animal_label in enumerate(animal_numbers):
                # select the period from period df and then split the
                # section df by that period
                period = name_df.loc[idx[condition_name,
                                         section], animal_label]
                split_df = split_dataframe_by_period(section_data,
                                                     drop_level=False,
                                                     reset_level=False,
                                                     animal_number=animal_no,
                                                     period=period)

                # save into dictionaries and dfs labelled by animal
                # / section / condition
                section_dict[animal_label] = split_df

            section_df = pd.concat(section_dict)
            condition_dict[section] = section_df

        condition_df = pd.concat(condition_dict)
        split_dict[condition_name] = condition_df

    split_all_condition_df = pd.concat(split_dict)

    return split_all_condition_df


# function to label cols for stats
def label_anim_cols(protocol_df,
                    level_index: int = 0):
    no_cols = len(protocol_df.columns)
    curr_protocol = protocol_df.index.get_level_values(level_index)[0]
    protocol_col_names = [str(curr_protocol +
                              str(x)
                              ) for x in range(1,
                                               (no_cols + 1)
                                               )]
    protocol_df.columns = protocol_col_names

    return protocol_df


def tukey_pairwise_ph(tidy_df,
                      hour_col: str = "Hour",
                      dep_var: str = "Value",
                      protocol_col: str = "Protocol"):
    """

    :type protocol_col: object
    """
    hours = tidy_df[hour_col].unique()
    ph_dict = {}
    for hour in hours:
        print(hour)
        hour_df = tidy_df.query("%s == '%s'" % (hour_col, hour))
        ph = pg.pairwise_tukey(dv=dep_var,
                               between=protocol_col,
                               data=hour_df)
        pg.print_table(ph)
        ph_dict[hour] = ph
    ph_df = pd.concat(ph_dict)

    return ph_df


def manual_resample_mean_groupby(curr_data,
                                 periods_df,
                                 mean: bool = True,
                                 sum: bool = False):
    types = curr_data.index.get_level_values(0).unique()
    protocols = curr_data.index.get_level_values(1).unique()
    times = curr_data.index.get_level_values(2).unique()
    animals = curr_data.index.get_level_values(3).unique()
    resampled_data_dict = {}
    for type in types:
        type_df = curr_data.loc[type]
        type_periods = periods_df.loc[type]
        type_dict = {}
        for protocol in protocols:
            protocol_df = type_df.loc[protocol]
            protocol_periods = type_periods.loc[protocol]
            protocol_dict = {}
            for time in times:
                time_df = protocol_df.loc[time]
                time_periods = protocol_periods.loc[time]
                time_dict = {}
                for animal in animals:
                    animal_df = time_df.loc[animal]
                    animal_period = time_periods.loc[animal]
                    if mean:
                        anim_day_df = animal_df.resample(animal_period).mean()
                    if sum:
                        anim_day_df = animal_df.resample(animal_period).sum()
                    time_dict[animal] = anim_day_df
                time_df_resampled = pd.concat(time_dict)
                protocol_dict[time] = time_df_resampled
            protocol_df_resampled = pd.concat(protocol_dict)
            type_dict[protocol] = protocol_df_resampled
        type_df_resampled = pd.concat(type_dict)
        resampled_data_dict[type] = type_df_resampled
    resampled_data = pd.concat(resampled_data_dict)

    return resampled_data


# function to set data by circadian period
def set_circadian_time(
        data,
        base_freq=4,
        period=24):
    """
    set_circadian_time
    Reindexes current data to 24 hours CT instead of ZT by setting
    frequency to the ratio of 24hrs/new period

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with a pandas timeindex
    base_freq : int
        sampling frequency of the data in seconds
    period : float
        new period to set the data to, in hours

    Returns
    -------
    pd.DataFrame
        original data but with new datetimeindex, starting at same time as
        original but now 24 hours is equal to the given period instead
        of real time.


    """
    # calculate what new frequency is
    freq_ratio = 24 / curr_period
    new_freq = base_freq * freq_ratio
    new_freq_str = str(np.round(new_freq * 1000)) + "ms"

    # create new index based on this
    start_time = data.index[0]
    data_length = len(data)
    new_index = pd.date_range(
        start=start_time,
        periods=data_length,
        freq=new_freq_str
    )

    # reindex the data
    reindexed_data = pd.DataFrame(
        data=data.values,
        index=new_index,
        columns=data.columns
    )

    return reindexed_data

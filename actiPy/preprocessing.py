import pdb
from functools import wraps
import pingouin as pg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
idx = pd.IndexSlice
# This script contains functions which are useful for preprocessing of
# actigraphy data

#### Decorators ####


def plot_kwarg_decorator(func):
    """
    Universal decorator for plot formatting and configuration.
    Handles xlabels, ylabels, titles, legends, time formatting, saving,
    and showing plots.
    :param func: The plotting function to decorate.
    :return: A decorated function that applies plot configurations.
    """
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        # Call the original plotting function
        fig, ax, params_dict = func(data, *args, **kwargs)

        # check if multiple subplots or not
        if isinstance(ax, (np.ndarray, list)):
            final_ax = ax[-1]
        else:
            final_ax = ax

        # Configure x-axis limits
        if "xlim" in kwargs or "xlim" in params_dict:
            xlim = kwargs.get("xlim", params_dict.get("xlim", None))
            if xlim:
                final_ax.set_xlim(xlim)

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
            final_ax.set_xlabel(
                    xlabel,
                    ha='center',
                    va='center')

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


def validate_input(func):
    """
    Decorator to validate DataFrames or Series passed to the function.
    - Checks if any input consists only of zeros.
    - Checks if any DataFrame is empty.
    - Checks if the index of any DataFrame is a DatetimeIndex.
    Raises a ValueError if any condition is not met.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Helper function to validate a DataFrame or Series
        def _validate(input_data, name):
            if isinstance(
                    input_data,
                    pd.DataFrame) or isinstance(
                        input_data,
                        pd.Series):
                # Check if consists only of zeros
                if (input_data.values == 0).all():
                    raise ValueError(f"Input {name} consists only of zeros.")

                # Check if empty
                if input_data.empty:
                    raise ValueError(f"Input {name} is empty.")

                # Check if index is a DatetimeIndex (only for DataFrames)
                if isinstance(
                        input_data,
                        pd.DataFrame) and not isinstance(
                            input_data.index,
                            pd.DatetimeIndex):
                    raise TypeError(
                        f"Input {name} does not have a DatetimeIndex.")

        # Validate positional arguments
        for i, arg in enumerate(args):
            _validate(arg, f"arg[{i}]")

        # Validate keyword arguments
        for key, value in kwargs.items():
            _validate(value, f"kwarg[{key}]")

        # Call the original function
        return func(*args, **kwargs)

    return wrapper


def invert_light_values(func):
    """
    Decorator to invert the light values in the given light column.
    Used to ensure that on plots, darkness is shaded grey, not the lights.

    Parameters
    ----------
    func : function
        The function to wrap.

    Returns
    -------
    function
        The wrapped function with inverted light values in the specified column.
    """
    @wraps(func)
    def wrapper(data, *args, light_col=-1, **kwargs):
        # Ensure light_col is a valid index
        if isinstance(light_col, int):  # If specified as column index
            light_col_name = data.columns[light_col]
        elif isinstance(light_col, str):  # If specified as column name
            light_col_name = light_col
        else:
            raise ValueError(
                "light_col must be an integer index or a column name")

        # Copy the data to avoid modifying the original DataFrame
        data = data.copy()

        # Invert the light values
        max_value = data[light_col_name].max()
        min_value = data[light_col_name].min()
        data[light_col_name] = max_value - data[light_col_name] + min_value

        # Call the original function with the modified data
        return func(data, *args, **kwargs)

    return wrapper


#### Functions ####
# function to set data by circadian period
@validate_input
def set_circadian_time(
        data,
        period='24h'):
    """
    Reindexes current data to 24 hours CT instead of ZT by setting
    frequency to the ratio of 24hrs/new period

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with a pandas timeindex
    period : str or float
        The new period to set the data to.
        Timedelta string (e.g., '24h', '1d', '72h')

    Returns
    -------
    pd.DataFrame
        Original data but with a new datetimeindex, starting at the same time
        as the original but now 24 hours is equal to the given period instead
        of real time.
    """

    # Convert period string to timedelta
    if isinstance(period, str):
        period = pd.to_timedelta(period)

    # Calculate the frequency ratio based on the period
    freq_ratio = 24 / (period.total_seconds() / 3600)

    # get data frequency as timedelta
    base_freq = pd.infer_freq(data.index)

    # Ensure base_freq has a numeric component
    if not any(char.isdigit() for char in base_freq):
        base_freq = '1' + base_freq  # Prepend '1' if missing

    # convert to timedelta
    base_timedelta = pd.to_timedelta(base_freq)

    # calculate ratio as a string
    new_timedelta = base_timedelta * freq_ratio
    new_freq_str = str(np.round(new_timedelta.total_seconds() * 1000)) + "ms"

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

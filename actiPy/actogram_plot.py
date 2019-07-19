import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import actiPy.preprocessing as prep
from actiPy.plots import multiple_plot_kwarg_decorator, \
    show_savefig_decorator, set_title_decorator

# function to create actogram plot

def actogram_plot_all_cols(data,
                           fname,
                           LDR=-1,
                           period="24H",
                           *args,
                           **kwargs):
    """
    Function to loop through each column of activity data
    and plot every column except for the LDR
    :param data:
    :param LDR:
    :param period: default "24H"
    :param args:
    :param kwargs: savefig, showfig, fname mainly
    :return:
    """
    # remove LDR column then call actogram plot from
    # df on each remaining column
    # and create new file name for each
    data_with_ldr = data.copy()
    ldr_data = data.pop(data.columns[LDR])
    
    for animal_no, label in enumerate(data.columns):
        file_name = fname.parent / (fname.stem +
                                    str(animal_no) +
                                    fname.suffix)
        _actogram_plot_from_df(data_with_ldr,
                              animal_number=animal_no,
                              period=period,
                              fname=file_name,
                              *args,
                              **kwargs)


def _actogram_plot_from_df(data,
                           animal_number,
                           LDR=-1,
                           period="24H",
                           drop_level=True,
                           *args,
                           **kwargs):
    """
    Function to apply LDR remap, then split the dataframe
    according to the given period, then plot the actogram
    :param data: dataframe of activity data
    :param animal_number: which column to plot
    :param LDR: which column has the light data
    :param args:
    :param kwargs:
    :return:
    """
    
    # remap the light data
    data_LDR_remap = prep.remap_LDR(data, drop_level=drop_level, **kwargs)
    
    if drop_level:
        # remove top level of the index
        data_LDR_remap.index = data_LDR_remap.index.droplevel(0)
    
    # split the dfs
    split_df_list = prep.split_entire_dataframe(data_LDR_remap,
                                                period=period)
    # plot with actogram
    fig, ax = _actogram_plot(split_df_list,
                             animal_number=animal_number,
                             LDR=LDR,
                             *args,
                             **kwargs)

    return fig, ax

@set_title_decorator
@multiple_plot_kwarg_decorator
def _actogram_plot(data,
                   animal_number=0,
                   LDR=-1,
                   ylim=[0, 120],
                   fig=False,
                   subplot=False,
                   ldralpha=0.5,
                   start_day=0,
                   day_label_size=5,
                   **kwargs):
    """
    Function to take in dataframe and plot a double-plotted actogram
    with lights shaded in
    :param data:
    :param animal_number:
    :param LDR:
    :param kwargs:
    :return:
    """

    # select the correct data
    data_to_plot = data[animal_number].copy()
    light_data = data[LDR].copy()

    # set up some constants
    NUM_DAYS = len(data_to_plot.columns)
    linewidth = 1
    if "linewidth" in kwargs:
        linewidth = kwargs["linewidth"]
        
    # add in values at the start and end
    # to let us double plot effectively
    for data in data_to_plot, light_data:
        data = pad_first_last_days(data)
        # set all 0 values to Nan
        data = convert_zeros(data, -100)

    
    # if not given a figure, just create the axes
    if not fig:
        fig, ax = plt.subplots(nrows=(NUM_DAYS+1))
    # create the ax list if given a figure and subplot to do it in.
    else:
        subplot_grid = gs.GridSpecFromSubplotSpec(nrows=(NUM_DAYS+1),
                                                  ncols=1,
                                                  subplot_spec=subplot,
                                                  wspace=0,
                                                  hspace=0)
        ax = []
        for grid in subplot_grid:
            sub_ax = plt.Subplot(fig, grid)
            fig.add_subplot(sub_ax)
            ax.append(sub_ax)

    # plot two days on each row
    for day_label, axis in zip(data_to_plot.columns[:-1], ax):
        # get two days of data to plot
        day_data = two_days(data_to_plot, day_label)
        day_light_data = two_days(light_data, day_label)
        
        # create masked data for fill between to avoid horizontal lines
        fill_data = day_data.where(day_data>0)
        fill_ldr = day_light_data.where(day_light_data>0)

        # plot the data and LDR
        axis.fill_between(fill_ldr.index,
                          fill_ldr,
                          alpha=ldralpha,
                          facecolor= "grey")
        axis.plot(day_data, linewidth=linewidth)
        axis.fill_between(fill_data.index,
                          fill_data)
          
        # need to hide all the axis to make visible
        axis.set(xticks=[],
                 xlim= [day_data.index[0],
                        day_data.index[-1]],
                 yticks=[],
                 ylim=ylim)
        spines = ["left", "right", "top", "bottom"]
        for pos in spines:
            axis.spines[pos].set_visible(False)
    
    if fig == False:
        fig.subplots_adjust(hspace=0)
    
    # create the y labels for every 10th row
    day_markers = np.arange(0,NUM_DAYS, 10)
    day_markers = day_markers + start_day
    for axis, day in zip(ax[::10], day_markers):
        axis.set_ylabel(day,
                        rotation=0,
                        va='center',
                        ha='right',
                        fontsize=day_label_size)
        
    # create defaults dict
    params_dict = {
        "xlabel": "Time",
        "ylabel": "Days",
        "interval": 6,
        "title": "Double Plotted Actogram",
        "timeaxis": True,
    }
    
    # put axis as a controllable parameter
    if "timeaxis" in kwargs:
        params_dict['timeaxis'] = kwargs["timeaxis"]
    
    return fig, ax[-1], params_dict


def pad_first_last_days(data):
    """
    Simple function to add a day to the start and end
    of the dataset consisting entirely of 0s
    Makes the actogram plots work as double plotted
    and not cutting off first and last days or
    stretching them
    :param data:
    :return:
    """
    NUM_BINS = len(data)
    NUM_DAYS = len(data.columns)
    # create a day of 0s and put at the start and the end
    zeros = np.zeros(NUM_BINS)
    data.insert(0, -1, zeros)
    data.insert((NUM_DAYS+1), (NUM_DAYS), zeros)
    return data
   
def convert_zeros(data, value):
    """
    Simple function to turn 0s into nans
    to make plotting look better
    as no line running along x axis
    :param data:
    :return:
    """
    data[data==0] = value
    return data

def two_days(data, day_one_label):
    """
    gets column of day label and day
    label plus one and returns the values
    as an array
    :param data:
    :param day_one_label:
    :return:
    """
    # get two days as a dataframe
    
    # grab the values of the first two days
    day_no = data.columns.get_loc(day_one_label)
    day_one = data.iloc[:,day_no]
    day_two = data.iloc[:,(day_no+1)]
    
    day_two.index = day_one.index + pd.Timedelta("1D")
    
    two_days = pd.concat([day_one, day_two])
    return two_days

#     How is this going to work? Needs the full df
#  so can take in the LDR data as well so
# then add in a day of 0s at the start and the end
# to make the first and the final day tidy
# then plot two days at a time

# Alternative is to take in the split list - and make sure t
# that the LDR is also split
# select based on the number in the list



# Function to plot actogram
# want to create split dataframe
# then try imshow?
# or plot.subplots?


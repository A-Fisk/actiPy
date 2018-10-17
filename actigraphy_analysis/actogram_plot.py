import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# function to create actogram plot

def actogram_plot(data,
                  animal_number,
                  LDR=-1,
                  *args,
                  **kwargs):
    """
    Function to create double plotted actogram from actigraphy
    data.
    :param data: list of dataframes where each has been
        split by the test period - given by output
        of the preprocessing.split_entire_dataframe
        function
    :param animal_number: int, which dataframe from
        the list of dataframes going to plot
    :param LDR: int, which dataframe from the list
        of dataframes is the light levels to plot
        in the background
    :param args:
    :param kwargs:
    :return:
    """
    # select the correct data
    data_to_plot = data[animal_number].copy()
    light_data = data[LDR].copy()
    
    # set up some constants
    NUM_BINS = len(data_to_plot)
    NUM_DAYS = len(data_to_plot.columns)
    
    # add in values at the start and end
    # to let us double plot effectively
    for data in data_to_plot, light_data:
        data = pad_first_last_days(data)
        # set all 0 values to Nan
        data = convert_zeros(data, -100)
    
    # data now ready to plot, have to create the plot
    # by looping through each day and plotting
    # this day and the next day, stopping at -1
    # only plotting the values though
    fig, ax = plt.subplots(nrows=(NUM_DAYS+1))
    for day_label, axis in zip(data_to_plot.columns[:-1], ax):
        # grab the values from the first two days to plot
        two_days_data = get_two_days_as_array(data_to_plot, day_label)
        two_days_lights = get_two_days_as_array(light_data, day_label)
        # create index to plot between
        index = range(0, len(two_days_data))
        axis.plot(index, two_days_data)
        axis.fill_between(index, two_days_data)
        axis.fill_between(index,
                          two_days_lights,
                          facecolor='grey',
                          alpha=0.5)
        # set parameters for current subplot
        axis.set(xticks=[],
                 ylim=[0,110],
                 yticks=[],
                 xlim=[0, len(two_days_data)])
        axis.set_frame_on(False)
        
    # set the xticks on the final plot
    xticks = np.linspace(plt.xlim()[0],
                         plt.xlim()[-1],
                         9)
    xlabels = [0,6,12,18,24,6,12,18,24]
    ax[-1].set(xticks=xticks,
               xticklabels=xlabels)
    
    # create the y labels for every 10th row
    day_markers = np.arange(0,NUM_DAYS, 10)
    for axis, day in zip(ax[::10], day_markers):
        axis.set_ylabel(day,
                        rotation=0,
                        va='center',
                        ha='right')
        
    # set parameters for figure
    fig.subplots_adjust(hspace=0)

    plt.show()
#  TODO write tests!
# TODO add in showfig and savefig options
    
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
    data.insert((NUM_DAYS+1), (NUM_DAYS+1), zeros)
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

def get_two_days_as_array(data, day_one_label):
    """
    gets column of day label and day
    label plus one and returns the values
    as an array
    :param data:
    :param day_one_label:
    :return:
    """
    day_no = data.columns.get_loc(day_one_label)
    day_one = data.iloc[:,day_no].values
    day_two = data.iloc[:,(day_no+1)].values
    two_days_array = np.append(day_one, day_two)
    return two_days_array

def remap_LDR(light_data, invert=True):
    """
    Takes values for an LDR where light on = high values
    and remaps to a where darkness is high values so
    can have darkness shaded on plot
    :param light_data:
    :param invert:
    :return:
    """
    # remap only between where the values are > 0 [0] and [-1]
    for day in light_data.columns:
        day_data = light_data.loc[:,day]
        if not (day_data>1).any():
            day_data = 200
            
    if (light_data.max() < 150).any():
        raise ValueError
    light_data[light_data>150] = 150
    if invert:
        light_data = 150-light_data
    return light_data



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
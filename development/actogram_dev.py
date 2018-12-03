# script to create actograms and save for all data files
# in input dir

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pathlib
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                    "07_python_package/actiPy")
import actiPy.preprocessing as prep
import actiPy.actogram_plot as act

input_directory = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/"
                                "01_projects/P2_Circ_Disruption_paper_chapt2/"
                                "01_data_files")
save_directory = input_directory.parent / "03_analysis_outputs"
subdir_name = '01_long_actograms'

file_list = sorted(input_directory.glob("*.csv"))
file = file_list[1]

init_kwargs = {
    "input_directory": input_directory,
    "save_directory": save_directory,
    "subdir_name": subdir_name,
    "func": (prep, "read_file_to_df"),
    "index_col": [1, 0],
    "header": [0]
}
df = prep.read_file_to_df(file, **init_kwargs)

# rewrite actogram plot

plot_kwargs = {
    "function": (act, "actogram_plot_all_cols"),
    "LDR": -1,
    "set_file_title": True,
    "showfig": True,
    "period": "24H"
}

act.actogram_plot_all_cols(df,
                           LDR=-1,
                           fname=file,
                           set_file_title=True,
                           period="24H",
                           showfig=True)

# first step get the right data to input, remap the LDR, remove top index,
# split based on period

# light_data = split_data[LDR].copy()
#
# # set up some constants
# NUM_BINS = len(data_to_plot)
# NUM_DAYS = len(data_to_plot.columns)
#
# # add in values at the start and end
# # to let us double plot effectively
# for data in data_to_plot, light_data:
#     data = act.pad_first_last_days(data)
#     # set all 0 values to Nan
#     data = act.convert_zeros(data, -100)
#
# # create the axes
# fig, ax = plt.subplots(nrows=(NUM_DAYS+1))
#
# # plot two days on each row
# for day_label, axis in zip(data_to_plot.columns[:-1], ax):
#     loc = data.columns.get_loc(day_label)
#     day_data = data_to_plot.iloc[:,loc]
#     axis.plot(day_data)
#
#     # need to hide all the axis to make visible
#     axis.set(xticks=[],
# #              xlim= [data_to_plot.index[0],
# #                     data_to_plot.index[-1]],
# #              yticks=[],
# #              ylim=[0, 120],)
# #     axis.axis('off')
# #
# # fig.subplots_adjust(hspace=0)
#
#
#
# from actiPy.plots import multiple_plot_kwarg_decorator, show_savefig_decorator
#
# @show_savefig_decorator
# @multiple_plot_kwarg_decorator
# def actogram_plot(data,
#                   animal_number=0,
#                   LDR=-1,
#                   **kwargs):
#
#     # select the correct data
#     data_to_plot = data[animal_number].copy()
#     light_data = data[LDR].copy()
#
#     # set up some constants
#     NUM_BINS = len(data_to_plot)
#     NUM_DAYS = len(data_to_plot.columns)
#
#     # add in values at the start and end
#     # to let us double plot effectively
#     for data in data_to_plot, light_data:
#         data = act.pad_first_last_days(data)
#         # set all 0 values to Nan
#         data = act.convert_zeros(data, -100)
#
#     # create the axes
#     fig, ax = plt.subplots(nrows=(NUM_DAYS+1))
#
#     # plot two days on each row
#     for day_label, axis in zip(data_to_plot.columns[:-1], ax):
#         # get two days of data to plot
#         day_data = act.two_days(data_to_plot, day_label)
#         day_light_data = act.two_days(light_data, day_label)
#
#         # plot the data and LDR
#         axis.plot(day_data)
#         axis.fill_between(day_data.index,
#                           day_data)
#         axis.fill_between(day_light_data.index,
#                           day_light_data,
#                           alpha= 0.5,
#                           facecolor= "grey")
#
#         # need to hide all the axis to make visible
#         axis.set(xticks=[],
#                  xlim= [day_data.index[0],
#                         day_data.index[-1]],
#                  yticks=[],
#                  ylim=[0, 120],)
#         spines = ["left", "right", "top", "bottom"]
#         for pos in spines:
#             axis.spines[pos].set_visible(False)
#
#     fig.subplots_adjust(hspace=0)
#
#     # create the y labels for every 10th row
#     day_markers = np.arange(0,NUM_DAYS, 10)
#     for axis, day in zip(ax[::10], day_markers):
#         axis.set_ylabel(day,
#                         rotation=0,
#                         va='center',
#                         ha='right')
#
#     # create defaults dict
#     params_dict = {
#         "xlabel": "Time",
#         "ylabel": "Days",
#         "interval": 6,
#         "title": "Double Plotted Actogram"
#     }
#
#     return fig, ax[-1], params_dict


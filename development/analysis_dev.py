# script to create actograms and save for all data files
# in input dir

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import seaborn as sns
sns.set()
import sys
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/07_python_package/"
                   "actiPy")
import actiPy.preprocessing as prep
import actiPy.analysis as als
from actiPy.plots import multiple_plot_kwarg_decorator, show_savefig_decorator

input_directory = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/"
                                "01_projects/P2_Circ_Disruption_paper_chapt2/"
                                "01_data_files/00_clean/")
save_directory = input_directory.parents[1] / "03_analysis_outputs"
subdir_name = '05_count_per_day'

init_kwargs = {
    "input_directory": input_directory,
    "save_directory": save_directory,
    "subdir_name": subdir_name,
    "func": (prep, "read_file_to_df"),
    "index_col": [0, 1],
    "header": [0]
}
test_object = prep.SaveObjectPipeline(**init_kwargs)

process_kwargs = {
    "function": (als, "count_per_day"),
    "create_df": True,
}
test_object.process_file(**process_kwargs)

plot_kwargs = {
    "function": (als, "pointplot_from_df"),
    "showfig": False,
    "savefig": True,
    "data_list": [test_object.processed_df],
    "file_list": [test_object.subdir_path.stem],
    "df": test_object.processed_df,
    "xlevel": 'light_period',
    "ylevel": "Activity_count_per_day",
    "groups": 'group',
    "dodge": True,
    "capsize": 0.1,
    "remove_col": False,
    "figsize": (10,10)
}
test_object.create_plot(**plot_kwargs)

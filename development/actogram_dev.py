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
from actiPy.plots import multiple_plot_kwarg_decorator, \
    show_savefig_decorator, set_title_decorator

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

plot_kwargs = {
    "function": (act, "actogram_plot_all_cols"),
    "LDR": -1,
    "set_file_title": True,
    "showfig": True,
    "period": "24H"
}


prep.slice_by_label_col()

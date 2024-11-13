import actigraphy_analysis.episodes as ep
import actigraphy_analysis.actogram_plot as act
import actigraphy_analysis.preprocessing as prep
import pathlib
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/actigraphy_analysis")

# read the first file in from the input directory
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/"
                         "01_Projects/P2_Circ_Disruption_paper_chapt2"
                         "/03_data_files/02_sleep")
file_name = list(input_dir.glob("*.csv"))[1]
data = prep.read_file_to_df(file_name)
test_fname = pathlib.Path('./test.png')

episodes = ep.create_episode_df(data,
                                min_length="20S")

bins = np.linspace(0, 100, 11)

ep.ep_hist_conditions_from_df(episodes,
                              showfig=True,
                              fname=file_name,
                              bins=bins,
                              logy=False)

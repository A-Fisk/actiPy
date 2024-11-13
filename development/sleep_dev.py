import actigraphy_analysis.sleep_process as sleep
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
                         "/03_data_files")
file_name = list(input_dir.glob("*.csv"))[0]
data = prep.read_file_to_df(file_name)

sleep_data = :

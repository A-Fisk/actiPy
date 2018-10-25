import pathlib
import sys
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/actigraphy_analysis")
import actigraphy_analysis.preprocessing as prep
import actigraphy_analysis.actogram_plot as act
import actigraphy_analysis.episode_finder as ep

# read the first file in from the input directory
input_dir = pathlib.Path("/Users/angusfisk/Documents/01_PhD_files/"
                         "01_Projects/P2_Circ_Disruption_paper_chapt2"
                         "/03_data_files")
file_name = list(input_dir.glob("*.csv"))[0]
data = prep.read_file_to_df(file_name)
data_nums = prep.remove_object_col(data)

# now to test the new function as we write it
episodes = ep.episode_find_df(data_nums)



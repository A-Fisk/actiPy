# Aim to create script for doing an enright periodogram

from Analysis_scripts import Equations_v2 as eq
import sys
import pandas as pd
import numpy as np

# import test data
activity_dir = pathlib.Path('/Users/angusfisk/Documents/01_PhD_files/'
                            '01_projects/01_thesisdata/02_circdis/'
                            '01_data_files/01_activity/00_clean')

activity_filenames = sorted(activity_dir.glob("*.csv"))

# import into lists
activity_dfs = prep.read_file_to_df(
    activity_filenames[0],
    index_col=index_cols)

# easy df just to work with
df = activity_dfs.loc["baseline"]

# now to re implement test - or just see if it will work?

sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/03_oldgithub/"
                   "GitHub/Analysis_files/Analysis_files/")


# see if class still working
qp_obj = eq.Circadian_Analysis(df)
qp_obj.Enright_Periodogram(low=20, high=30)

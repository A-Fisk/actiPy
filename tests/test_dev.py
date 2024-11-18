import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if True:  # noqa E402
    import actiPy.activity as act
    import actiPy.preprocessing as prep
    import actiPy.actogram_plot as actp
    from tests.activity_tests import assign_values

# Create time index for 10 days with 10-second intervals
days = 10
freq = '10s'
time_index = pd.date_range(start='2000-01-01', periods=8640 * days, freq=freq)

# Create an empty DataFrame
df = pd.DataFrame(index=time_index)

# Function to assign values based on time of day


# create activity columns
act_night = [0, 10]
act_day = [10, 100]
light_night = [0, 1]
light_day = [500, 501]
df['sensor1'] = df.index.hour.map(
    lambda x: assign_values(x, act_day, act_night))
df['sensor2'] = df.index.hour.map(
    lambda x: assign_values(x, act_night, act_day))
df['lights'] = df.index.hour.map(
    lambda x: assign_values(x, light_night, light_day))
# Display the first few rows of the DataFrame
print(df.head())

# test actogram plot with invert light values
fig, ax, params_dict = actp.plot_activity_profile(
    df, showfig=True, resample=True, resample_freq='h')

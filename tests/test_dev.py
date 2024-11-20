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
    import actiPy.periodogram as per
    from tests.activity_tests import assign_values

# Create time index for 10 days with 10-second intervals
days = 100
freq = '10s'
time_index = pd.date_range(start='2000-01-01', periods=8640 * days, freq=freq)

# Create an empty DataFrame
df = pd.DataFrame(index=time_index)

# Function to assign values based on time of day


# create activity columns
act_night = [0, 5]
act_day = [50, 100]
light_night = [0, 1]
light_day = [500, 501]
df['sensor1'] = df.index.hour.map(
    lambda x: assign_values(x, act_night, act_day))
df['sensor2'] = df.index.hour.map(
    lambda x: assign_values(x, act_night, act_day))
df['lights'] = df.index.hour.map(
    lambda x: assign_values(x, light_night, light_day))
# Display the first few rows of the DataFrame
print(df.head())

# test lomb scargle

constant_data = pd.DataFrame(
    {"sensor1": [1] * len(df)}, index=df.index)
constant_pmax = 3.12e-5

power = per.lomb_scargle_period(df, high_period=30)

power_df = power["Power_values"]

fig, ax = plt.subplots()
ax.plot(power_df.index, power_df.values)
fig.show()

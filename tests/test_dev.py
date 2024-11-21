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
days = 10
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
# Generate a sine wave for sensor3 with a 24-hour period
# The time is in seconds, so we use the modulo of the day (24 hours) to
# generate the sine wave
time_in_seconds = (
    df.index.hour * 3600 + df.index.minute * 60 + df.index.second) / 86400
# sine wave with 24-hour period
sensor3_sine_wave = np.sin(2 * np.pi * time_in_seconds)
# Scale the sine wave to be between 0 and 100
# Shift by 1 to make it between 0 and 2, then scale by 50
df["sensor3"] = (sensor3_sine_wave + 1) * 50
df['lights'] = df.index.hour.map(
    lambda x: assign_values(x, light_night, light_day))

# Display the first few rows of the DataFrame
print(df.head())
data = df
subject_no = 0

# select the data
curr_data = data.iloc[:, subject_no]

# calculate mean
mean_data = act.calculate_mean_activity(curr_data)

# sum of squares from the mean
mean = curr_data.mean()


# test calculate_IS
IS = act.calculate_IS(df, subject_no=2)

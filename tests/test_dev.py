import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if True:  # noqa E402
    import actiPy.activity as act
    import actiPy.preprocessing as prep
    import actiPy.actogram_plot as actp

# Create time index for 10 days with 10-second intervals
days = 10
freq = '10s'
time_index = pd.date_range(start='2000-01-01', periods=8640 * days, freq=freq)

# Create an empty DataFrame
df = pd.DataFrame(index=time_index)

# Function to assign values based on time of day


def assign_values(hour, night, day):
    if 6 <= hour < 18:  # Between 06:00 and 18:00
        return np.random.randint(night[0], night[1])
    else:  # Between 18:00 and 06:00
        return np.random.randint(day[0], day[1])


# create activity columns
act_night = [0, 10]
act_day = [10, 100]
light_night = [0, 1]
light_day = [500, 501]
df['sensor1'] = df.index.hour.map(
    lambda x: assign_values(x, act_day, act_day))
df['sensor2'] = df.index.hour.map(
    lambda x: assign_values(x, act_night, act_day))
df['lights'] = df.index.hour.map(
    lambda x: assign_values(x, light_night, light_day))
# Display the first few rows of the DataFrame
print(df.head())

# Sample data for testing
index = pd.date_range("2024-01-01", "2024-01-02", freq="h")
test_data = pd.DataFrame({
    # Linearly increasing activity
    "Activity1": np.linspace(1, 24, len(index)),
    # Linearly decreasing activity
    "Activity2": np.linspace(24, 1, len(index)),
    "Light": np.random.randint(0, 100, len(index))  # Random activity
}, index=index)

rel_amp = act.relative_amplitude(test_data)

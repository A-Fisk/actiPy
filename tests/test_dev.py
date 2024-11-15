import actiPy.actogram_plot as act
import actiPy.preprocessing as prep
import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
act_night = [0,10]
act_day = [10, 100]
light_night = [0,1]
light_day = [500,501]
df['sensor1'] = df.index.hour.map(
        lambda x: assign_values(x, act_night, act_day))
df['sensor2'] = df.index.hour.map(
        lambda x: assign_values(x, act_night, act_day))
df['lights'] = df.index.hour.map(
        lambda x: assign_values(x, light_night, light_day))
# Display the first few rows of the DataFrame
print(df.head())


# okay so now ... test that?
actogram, ax = act._actogram_plot(df, set_file_title=False)
actogram.show()

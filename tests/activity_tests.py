import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from datetime import datetime
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if True:  # noqa E402
    import actiPy.activity as act


np.random.seed(42)


class TestCalculateMeanActivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests."""
        # Create time index for 10 days with 10-second intervals
        days = 10
        freq = "10s"
        time_index = pd.date_range(
            start="2000-01-01",
            periods=8640 * days,
            freq=freq)

        # Create an empty DataFrame
        df = pd.DataFrame(index=time_index)

        # Function to assign values based on time of day
        def assign_values(hour, night, day):
            if 6 <= hour < 18:  # Between 06:00 and 18:00
                return np.random.randint(night[0], night[1])
            else:  # Between 18:00 and 06:00
                return np.random.randint(day[0], day[1])

        # Create activity and light columns
        act_night = [0, 10]
        act_day = [10, 100]
        light_night = [0, 1]
        light_day = [500, 501]
        df["sensor1"] = df.index.hour.map(
            lambda x: assign_values(x, act_night, act_day)
        )
        df["sensor2"] = df.index.hour.map(
            lambda x: assign_values(x, act_night, act_day)
        )
        df["lights"] = df.index.hour.map(
            lambda x: assign_values(x, light_night, light_day)
        )
        cls.test_data = df

    def test_calculate_mean_activity(self):
        """Test mean activity calculation."""
        result = calculate_mean_activity(self.test_data)
        self.assertIsInstance(
            result,
            pd.DataFrame,
            "The result should be a DataFrame.")
        self.assertFalse(result.empty, "The result should not be empty.")
        self.assertTrue(
                all(isinstance(i, datetime.time) for i in result.index),
                "The index of the result should be times (ignoring dates).")

    def test_invalid_index(self):
        """Test the function with a non-DatetimeIndex."""
        invalid_data = pd.DataFrame({'activity': [1, 2, 3]}, index=[1, 2, 3])
        with self.assertRaises(TypeError):
            calculate_mean_activity(invalid_data)

    def test_empty_dataframe(self):
        """Test the function with an empty DataFrame."""
        empty_data = pd.DataFrame({'activity': []}, index=pd.DatetimeIndex([]))
        with self.assertRaises(ValueError):
            calculate_mean_activity(empty_data)



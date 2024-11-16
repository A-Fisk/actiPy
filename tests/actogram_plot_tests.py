import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs 
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import actiPy.actogram_plot as act

np.random.seed(42)

class TestPlotActogram(unittest.TestCase):
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

    def test_plot_actogram_basic(self):
        """Test that plot_actogram runs without errors on valid input."""
        data = self.test_data
        fig, ax, params_dict = act.plot_actogram(data, subject_no=0, LDR=-1)

        self.assertIsInstance(
            fig,
            plt.Figure,
            "Returned fig is not a matplotlib Figure.")
        self.assertIsInstance(
            ax[-1], plt.Axes, "Returned ax is not a matplotlib Axes.")
        self.assertIsInstance(
            params_dict,
            dict,
            "Returned params_dict is not a dictionary.")

    def test_plot_actogram_empty_data(self):
        """Test empty data"""
        # Empty DataFrame
        empty_data = pd.DataFrame(
            columns=[
                "sensor1",
                "lights"],
            index=pd.date_range(
                "2000-01-01",
                periods=0,
                freq="10min"))
        with self.assertRaises(ValueError):
            act.plot_actogram(empty_data, subject_no=0, LDR=-1)

    def test_plot_actogram_single_day(self):
        """Test for single day of data""" 
        # Single-day DataFrame
        # First day's worth of data (10s intervals)
        start = self.test_data.index[0]
        end = start + pd.Timedelta("24h")
        single_day_data = self.test_data.loc[start:end]
        fig, ax, params_dict = act.plot_actogram(
            single_day_data, subject_no=0, LDR=-1)
        self.assertIsInstance(
            fig,
            plt.Figure,
            "Single-day test failed to produce a valid figure.")

    def test_plot_actogram_invalid_params(self):
        """Test invalid parameter inputs."""
        data = self.test_data

        with self.assertRaises(IndexError):
            # Invalid subject_no
            act.plot_actogram(data, subject_no=10, LDR=-1)

        with self.assertRaises(IndexError):
            # Invalid LDR
            act.plot_actogram(data, subject_no=0, LDR=10)

    def test_plot_actogram_output_labels(self):
        """Test that the plot includes expected labels and titles."""
        data = self.test_data
        fig, ax, params_dict = act.plot_actogram(data, subject_no=0, LDR=-1)

        # Check defaults in params_dict
        self.assertEqual(
            params_dict["xlabel"],
            "Time",
            "X-axis label mismatch.")
        self.assertEqual(
            params_dict["ylabel"],
            "Days",
            "Y-axis label mismatch.")
        self.assertIn(
            "Double Plotted Actogram",
            params_dict["title"],
            "Title mismatch.")

    def test_plot_actogram_multiple_days(self):
        """Test that plotting works for multiple days."""
        data = self.test_data
        fig, ax, params_dict = act.plot_actogram(data, subject_no=0, LDR=-1)
        
        days_count = len(data.index.normalize().unique()) + 1
        self.assertEqual(
            len(ax),
            days_count,
            "Number of axes does not match expected number of days.")

    def test_plot_actogram_subplotting(self):
        """Test that can plot on subplot"""
        data = self.test_data
        fig = plt.figure()
        ax = fig.add_gridspec(ncols=2, nrows=2)
        fig, ax, params_dict = act.plot_actogram(
                data, subject_no=0, LDR=-1, fig=fig, subplot=ax[0], 
                title="subplots test")
        
        self.assertIsInstance(
            fig,
            plt.Figure,
            "Subplots test failed to produce a valid figure.")

    def test_plot_actogram_frequencies(self):
        """Test that can handle different frequencies"""
        data = self.test_data
        data_mins = data.resample("1min").mean()
        data_hours = data.resample("1h").mean()

        for curr_data in data_mins, data_hours: 
            fix, ax, params_dict = act.plot_actogram(
                    curr_data, subject_no=0, LDR=-1) 

            days_count = len(curr_data.index.normalize().unique()) + 1
            self.assertEqual(
                len(ax),
                days_count,
                "Number of axes does not match expected number of days.")


if __name__ == "__main__":
    unittest.main()

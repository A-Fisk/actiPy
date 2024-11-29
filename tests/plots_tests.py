import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
from unittest.mock import patch
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if True:  # noqa E402
    from circaPy.plots import plot_actogram, plot_activity_profile
    from circaPy.preprocessing import set_circadian_time
    from tests.activity_tests import assign_values, generate_test_data


np.random.seed(42)


class TestPlotActogram(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests."""
        cls.test_data = generate_test_data()

    def test_plot_actogram_basic(self):
        """Test that plot_actogram runs without errors on valid input."""
        data = self.test_data
        fig, ax, params_dict = plot_actogram(data, subject_no=0, light_col=-1)

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
            plot_actogram(empty_data, subject_no=0, light_col=-1)

    def test_plot_actogram_single_day(self):
        """Test for single day of data"""
        # Single-day DataFrame
        # First day's worth of data (10s intervals)
        start = self.test_data.index[0]
        end = start + pd.Timedelta("24h")
        single_day_data = self.test_data.loc[start:end]
        fig, ax, params_dict = plot_actogram(
            single_day_data, subject_no=0, light_col=-1)
        self.assertIsInstance(
            fig,
            plt.Figure,
            "Single-day test failed to produce a valid figure.")

    def test_plot_actogram_invalid_params(self):
        """Test invalid parameter inputs."""
        data = self.test_data

        with self.assertRaises(IndexError):
            # Invalid subject_no
            plot_actogram(data, subject_no=10, light_col=-1)

        with self.assertRaises(IndexError):
            # Invalid light_col
            plot_actogram(data, subject_no=0, light_col=10)

    def test_plot_actogram_output_labels(self):
        """Test that the plot includes expected labels and titles."""
        data = self.test_data
        fig, ax, params_dict = plot_actogram(data, subject_no=0, light_col=-1)

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
        fig, ax, params_dict = plot_actogram(data, subject_no=0, light_col=-1)

        days_count = len(data.index.normalize().unique()) + 1
        self.assertEqual(
            len(ax),
            days_count,
            "Number of axes does not match expected number of days.")

    def test_plot_actogram_subplotting(self):
        """Test that can plot on subplot"""
        data = self.test_data
        fig, ax = plt.subplots(ncols=2)
        subplot = ax[1]
        fig, ax, params_dict = plot_actogram(
            data, subject_no=0, light_col=-1, fig=fig, subplot=subplot,
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
            fix, ax, params_dict = plot_actogram(
                curr_data, subject_no=0, light_col=-1)

            days_count = len(curr_data.index.normalize().unique()) + 1
            self.assertEqual(
                len(ax),
                days_count,
                "Number of axes does not match expected number of days.")

    def test_non_24hr_day(self):
        """Tests can handle non-24 hour days"""
        data = self.test_data
        data_twenty = set_circadian_time(data, period="20h")
        fig, ax, params_dict = plot_actogram(data_twenty, title="20hr test")
        days_twenty = len(data_twenty.index.normalize().unique()) + 1
        self.assertEqual(
            len(ax),
            days_twenty,
            "Number of axes does not match expected number of days.")


class TestPlotActivityProfile(unittest.TestCase):

    def setUp(self):
        # Generate test data using the provided function
        self.df = generate_test_data(
            days=10, freq="10s", act_night=[
                0, 10], act_day=[
                10, 100])

    def test_plot_activity_profile_without_resampling(self):
        # Test the function without resampling
        fig, ax, params = plot_activity_profile(
            self.df, col=0, resample=False)

        # Check that the figure and ax are created
        self.assertIsInstance(fig, plt.Figure)
        self.assertIsInstance(ax, plt.Axes)

        # Check that params dictionary contains expected keys
        self.assertIn("xlabel", params)
        self.assertIn("ylabel", params)
        self.assertIn("xlim", params)

        # Check that xlim is correct (start of the datetime index and 24h
        # period)
        self.assertEqual(
            params["xlim"][0],
            pd.Timestamp('2001-01-01 00:00:05'))
        self.assertEqual(
            params["xlim"][1],
            pd.Timestamp('2001-01-02 00:00:05'))

    def test_plot_activity_profile_with_resampling(self):
        # Test the function with resampling
        fig, ax, params = plot_activity_profile(
            self.df, col=0, resample=True, resample_freq='D')

        # Check that the figure and ax are created
        self.assertIsInstance(fig, plt.Figure)
        self.assertIsInstance(ax, plt.Axes)

        # Check that the data has been resampled
        # 10 days of data, resampled daily
        self.assertEqual(len(self.df.resample('D').mean()), 10)
        self.assertEqual(len(ax.lines), 1)  # Only one plot line (mean)

    def test_resample_freq(self):
        # Test the resample frequency functionality
        fig, ax, params = plot_activity_profile(
            self.df, col=0, resample=True, resample_freq='min')

        # Get the x-axis data (time points)
        x_data = ax.lines[0].get_xdata()

        # Check if the number of data points is equal to the
        # number of minutes in a day (1440)
        self.assertEqual(len(x_data), 1440)  # 1440 minutes in a day
        self.assertEqual(len(ax.lines), 1)  # Only one plot line (mean)

    def test_plot_with_invalid_column_index(self):
        # Test with invalid column index (out of range)
        with self.assertRaises(IndexError):
            plot_activity_profile(self.df, col=5)

    def test_plot_with_invalid_resample_freq(self):
        # Test that an invalid resample frequency raises an error
        with self.assertRaises(ValueError):
            plot_activity_profile(
                self.df,
                col=0,
                resample=True,
                resample_freq='invalid_freq')

    @patch('matplotlib.pyplot.show')
    def test_plot_activity_profile_plot_called(self, mock_show):
        # Test if plot is displayed
        fig, ax, params = plot_activity_profile(
            self.df, col=0, resample=False, showfig=True)

        # Check that show is called (i.e., the plot is displayed)
        mock_show.assert_called_once()

    def test_xlim_correctness_after_resampling(self):
        # Test that xlim is correctly set after resampling
        fig, ax, params = plot_activity_profile(
            self.df, col=0, resample=True, resample_freq='h')

        # Check if xlim matches the expected range after resampling
        expected_xlim = [
            pd.Timestamp('2001-01-01 00:30:00'),
            pd.Timestamp('2001-01-02 00:30:00')]
        self.assertEqual(params["xlim"], expected_xlim)


if __name__ == "__main__":
    unittest.main()

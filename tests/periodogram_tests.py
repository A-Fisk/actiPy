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
    from circaPy.periodogram import lomb_scargle_period
    from circaPy.preprocessing import set_circadian_time
    from tests.activity_tests import assign_values, generate_test_data


class TestLombScarglePeriod(unittest.TestCase):

    def setUp(self):
        """Set up test data using `generate_test_data`."""
        self.data = generate_test_data(days=10, freq="10s")

    def test_valid_input(self):
        """Test the function with valid input."""
        result = lomb_scargle_period(
            self.data,
            subject_no=0,
            low_period=20,
            high_period=30)
        self.assertIn("Pmax", result)
        self.assertIn("Period", result)
        self.assertIn("Power_values", result)
        self.assertGreater(result["Pmax"], 0)
        self.assertEqual(24, np.round(result["Period"]))

    def test_invalid_subject_no(self):
        """Test with an invalid subject_no."""
        with self.assertRaises(IndexError):
            lomb_scargle_period(self.data, subject_no=10)

    def test_low_period_greater_than_high_period(self):
        """Test with low_period >= high_period."""
        with self.assertRaises(ValueError):
            lomb_scargle_period(self.data, low_period=30, high_period=20)

    def test_empty_dataframe(self):
        """Test with an empty DataFrame."""
        empty_data = pd.DataFrame()
        with self.assertRaises(ValueError):
            result = lomb_scargle_period(empty_data)

    def test_all_nan_column(self):
        """Test with a column containing all NaNs."""
        nan_data = pd.DataFrame(
            {"sensor1": [np.nan] * len(self.data)}, index=self.data.index)
        result = lomb_scargle_period(nan_data, subject_no=0)
        self.assertEqual(result["Pmax"], 0)
        self.assertTrue(pd.isna(result["Period"]))
        self.assertTrue(result["Power_values"].empty)

    def test_single_value_column(self):
        """Test with a column containing a single repeated value."""
        constant_data = pd.DataFrame(
            {"sensor1": [1] * len(self.data)}, index=self.data.index)
        result = lomb_scargle_period(constant_data, subject_no=0)
        self.assertTrue(result["Pmax"] < 0.1)

    def test_power_values_structure(self):
        """Test that Power_values is a non-empty pd.Series with the correct index."""
        result = lomb_scargle_period(
            self.data,
            subject_no=0,
            low_period=20,
            high_period=30)
        power_values = result["Power_values"]
        self.assertIsInstance(power_values, pd.Series)
        self.assertGreater(len(power_values), 0)
        self.assertTrue(
            (20 <= power_values.index).all() and (
                power_values.index <= 30).all())

    def test_twenty_hrs(self):
        """Test can detect a 20 hour period"""
        data = self.data
        data_circ = set_circadian_time(data, period="28h")
        result = lomb_scargle_period(
            data_circ,
            subject_no=0,
            low_period=20,
            high_period=30)
        self.assertTrue(result["Period"] < 21)


if __name__ == "__main__":
    unittest.main()

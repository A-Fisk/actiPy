import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import datetime
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if True:  # noqa E402
    from tests.activity_tests import assign_values, generate_test_data
    from actiPy.preprocessing import set_circadian_time


class TestSetCircadianTime(unittest.TestCase):

    def setUp(self):
        """Set up sample data for testing using the provided functions"""
        # Generate test data with 10 days of data at 10-second intervals
        self.data = generate_test_data(
            days=10, freq="10s", act_night=[
                0, 10], act_day=[
                10, 100], light_night=[
                0, 1], light_day=[
                    500, 501])

    def test_set_circadian_time_with_str_period(self):
        """Test if the function handles string period (e.g., '24h') correctly"""
        period = '24h'
        result = set_circadian_time(self.data, period)

        # Ensure the result has the same number of rows as the original data
        self.assertEqual(len(result), len(self.data))

        # Check the new frequency (should be approximately hourly)
        self.assertTrue(result.index.freqstr in ['10000ms'])

    def test_set_circadian_time_with_other_timedelta(self):
        """Test if the function handles other timedelta periods (e.g., '72h') correctly"""
        period = '72h'
        result = set_circadian_time(self.data, period)

        # Ensure the result has the same number of rows as the original data
        self.assertEqual(len(result), len(self.data))

        # Check the new frequency (should be 3333ms for '72h' period)
        self.assertTrue(result.index.freqstr in ['3333ms'])

    def test_set_circadian_time_with_nonstandard_period(self):
        """Test if the function handles non-standard periods (e.g., '1d') correctly"""
        period = '1d'  # equivalent to 24 hours
        result = set_circadian_time(self.data, period)

        # Ensure the result has the same number of rows as the original data
        self.assertEqual(len(result), len(self.data))

        # Check the new frequency (should be approximately 10000ms for '1d')
        self.assertTrue(result.index.freqstr in ['10000ms'])

    def test_set_circadian_time_with_invalid_period(self):
        """Test if the function raises an error for invalid period inputs"""
        period = 'invalid_period'

        # Check if ValueError is raised for invalid period string
        with self.assertRaises(ValueError):
            set_circadian_time(self.data, period)

    def test_set_circadian_time_with_no_period(self):
        """Test if the function uses default period when none is provided"""
        result = set_circadian_time(self.data)

        # Ensure the result has the same number of rows as the original data
        self.assertEqual(len(result), len(self.data))

        # Check the default period is '24h'
        self.assertTrue(result.index.freqstr in ['10000ms'])

    def test_set_circadian_time_frequency_preservation(self):
        """Test if the frequency of the resulting data is correctly adjusted"""
        period = '48h'  # 48 hours as the new period
        result = set_circadian_time(self.data, period)

        # Ensure the new frequency matches the expected adjustment
        # 5000ms should be the new frequency
        self.assertTrue(result.index.freqstr in ['5000ms'])

    def test_set_circadian_time_with_alternate_freq(self):
        """Test if the function handles non-evenly sampled data correctly"""
        # Generate data at a 1-minute frequency (uneven sampling)
        data_uneven = generate_test_data(
            days=5, freq="1min", act_night=[
                0, 10], act_day=[
                10, 100], light_night=[
                0, 1], light_day=[
                    500, 501])

        period = '48h'
        result = set_circadian_time(data_uneven, period)

        # Ensure the result has the same number of rows as the original data
        self.assertEqual(len(result), len(data_uneven))

        # Check the new frequency (should be 30000ms intervals for '48h'
        # period)
        self.assertTrue(result.index.freqstr in ['30000ms'])


if __name__ == '__main__':
    unittest.main()

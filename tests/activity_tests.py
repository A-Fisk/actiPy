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
    from actiPy.activity import calculate_mean_activity, calculate_IV, \
            normalise_to_baseline


np.random.seed(42)

# functions to simulate data


def assign_values(hour, night, day):
    """
    Assigns values based on the hour of the day.

    Parameters
    ----------
    hour : int
        The hour of the day (0-23).
    night : list
        Range [min, max) for values during night hours.
    day : list
        Range [min, max) for values during day hours.

    Returns
    -------
    int
        A value based on the hour of the day.
    """
    if 6 <= hour < 18:  # Between 06:00 and 18:00
        return np.random.randint(day[0], day[1])
    else:  # Between 18:00 and 06:00
        return np.random.randint(night[0], night[1])


def generate_test_data(days=10, freq="10s"):
    """
    Generate test data for activity and light levels.

    Parameters
    ----------
    days : int, optional
        Number of days to generate data for. Default is 10.
    freq : str, optional
        Frequency of the time intervals. Default is "10s" (10 seconds).

    Returns
    -------
    pd.DataFrame
        A DataFrame with a datetime index and columns for `sensor1`, `sensor2`,
        and `lights` data.
    """
    # Create a time index for the specified number of days
    time_index = pd.date_range(
        start="2000-01-01", periods=8640 * days, freq=freq
    )

    # Create an empty DataFrame
    df = pd.DataFrame(index=time_index)

    # Define activity and light ranges
    act_night = [0, 10]
    act_day = [10, 100]
    light_night = [0, 1]
    light_day = [500, 501]

    # Populate the DataFrame with sensor and light data
    df["sensor1"] = df.index.hour.map(
        lambda x: assign_values(x, act_night, act_day)
    )
    df["sensor2"] = df.index.hour.map(
        lambda x: assign_values(x, act_night, act_day)
    )
    df["lights"] = df.index.hour.map(
        lambda x: assign_values(x, light_night, light_day)
    )

    return df


class TestCalculateMeanActivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests."""
        cls.test_data = generate_test_data(days=10, freq="10s")

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


class TestCalculateIV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests."""
        cls.test_data = generate_test_data(days=10, freq="10s")

    def test_calculate_IV_valid_data(self):
        """Test IV calculation on valid data."""
        iv_sensor1 = calculate_IV(self.test_data["sensor1"])
        iv_sensor2 = calculate_IV(self.test_data["sensor2"])

        self.assertIsInstance(
            iv_sensor1,
            float,
            "IV result for sensor1 should be a float.")
        self.assertIsInstance(
            iv_sensor2,
            float,
            "IV result for sensor2 should be a float.")
        self.assertGreater(
            iv_sensor1,
            0,
            "IV result for sensor1 should be positive.")
        self.assertGreater(
            iv_sensor2,
            0,
            "IV result for sensor2 should be positive.")

    def test_empty_data(self):
        """Test IV calculation on empty data."""
        with self.assertRaises(ValueError):
            calculate_IV([])

    def test_single_data_point(self):
        """Test IV calculation with a single data point."""
        with self.assertRaises(ValueError):
            calculate_IV([10])

    def test_identical_values(self):
        """Test IV calculation with all identical values."""
        data = [5] * 100  # All values are the same
        result = calculate_IV(data)
        self.assertEqual(result, 0, "IV should be 0 for identical values.")

    def test_linear_increasing_data(self):
        """Test IV calculation with a linearly increasing dataset."""
        data = np.arange(100)  # Linear increase
        result = calculate_IV(data)
        self.assertGreater(result, 0, "IV should be positive for linear data.")

    def test_random_data(self):
        """Test IV calculation with random data."""
        data = np.random.randint(0, 100, size=100)
        result = calculate_IV(data)
        self.assertGreater(result, 0, "IV should be positive for random data.")
        self.assertIsInstance(result, float, "IV result should be a float.")

    def test_dataframe_input(self):
        """Test IV calculation when passing a DataFrame column."""
        iv_lights = calculate_IV(self.test_data["lights"])
        self.assertIsInstance(iv_lights, float, "IV result should be a float.")
        self.assertGreater(
            iv_lights,
            0,
            "IV result for lights should be positive.")


class TestNormaliseToBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data for all tests."""
        # Generate test data for multiple days
        cls.data = generate_test_data(days=10, freq="10s")

    def test_normalisation_valid_data(self):
        """Test normalisation with valid data."""
        test_data = self.data.iloc[:,0]
        test_data_baseline = self.data.iloc[:,1]
    
        normalised_data = normalise_to_baseline(test_data, test_data_baseline)

        # Check that the result is a DataFrame or Series
        self.assertIsInstance(
            normalised_data,
            pd.Series,
            "Result should be a Series.")
        pdb.set_trace()

        # Check that the index is retained
        self.assertTrue(
            (normalised_data.index == self.data.index).all(),
            "The index of the normalised data should match the original data.",
        )

    def test_zero_baseline_data(self):
        """Test handling of zero baseline values."""
        test_data = self.data.iloc[:,0]
        baseline_data_zero = self.data.iloc[:,1]
        
        baseline_data_zero.iloc[:] = 0  # Set baseline to zero

        with self.assertRaises(ZeroDivisionError):
            normalise_to_baseline(
                test_data, baseline_data_zero)   
            

    def test_empty_data(self):
        """Test normalisation with empty data."""
        empty_data = pd.Series(dtype=float, name="sensor1")
        empty_baseline = pd.Series(dtype=float, name="sensor1")

        with self.assertRaises(ValueError):
            normalise_to_baseline(empty_data, empty_baseline)

    def test_partial_zero_baseline(self):
        """Test handling of partial zero baseline values."""
        test_data = self.data.iloc[:,0]
        baseline_data_partial_zero = self.data.iloc[:,1]
        baseline_data_partial_zero.iloc[0] = 0  # Set the first value to zero

        with self.assertRaises(ZeroDivisionError):
            normalise_to_baseline(
                test_data, baseline_data_partial_zero
            )

    def test_identical_data(self):
        """Test normalisation when data and baseline are identical."""
        test_data = self.data.iloc[:,0]
        result = normalise_to_baseline(
            test_data, test_data
        )
        self.assertTrue(
            (result == 100).all(),
            "When data and baseline are identical, all values should be 100.",
        )


if __name__ == "__main_":
    unittest.main()

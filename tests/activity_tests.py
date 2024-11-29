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
    from circaPy.activity import calculate_mean_activity, calculate_IV, \
        normalise_to_baseline, light_phase_activity, relative_amplitude, \
        calculate_IS, calculate_TV


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


def generate_test_data(days=10,
                       freq="10s",
                       act_night=[0, 10],
                       act_day=[10, 100],
                       light_night=[0, 1],
                       light_day=[500, 501]):
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

    # Populate the DataFrame with sensor and light data
    df["sensor1"] = df.index.hour.map(
        lambda x: assign_values(x, act_night, act_day)
    )
    df["sensor2"] = df.index.hour.map(
        lambda x: assign_values(x, act_night, act_day)
    )
    # 24 hour sine wave between 0-100 for sensor 3
    time_in_seconds = (
        df.index.hour * 3600 + df.index.minute * 60 + df.index.second) / 86400
    sensor3_sine_wave = np.sin(2 * np.pi * time_in_seconds)
    df["sensor3"] = (sensor3_sine_wave + 1) * 50

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
    def setUpClass(self):
        """Set up test data for all tests."""
        # Generate test data for multiple days
        self.data = generate_test_data(days=10, freq="10s")
        self.test_data = self.data.iloc[:, 0]
        self.test_data_baseline = self.data.iloc[:, 1]

    def test_normalisation_valid_data(self):
        """Test normalisation with valid data."""
        normalised_data = normalise_to_baseline(
            self.test_data, self.test_data_baseline)

        # Check that the result is a DataFrame or Series
        self.assertIsInstance(
            normalised_data,
            pd.Series,
            "Result should be a Series.")

        # Check that the index is retained
        self.assertTrue(
            (normalised_data.index == self.data.index).all(),
            "The index of the normalised data should match the original data.",
        )

    def test_empty_data(self):
        """Test normalisation with empty data."""
        empty_data = pd.Series(dtype=float, name="sensor1")
        empty_baseline = pd.Series(dtype=float, name="sensor1")

        with self.assertRaises(ValueError):
            normalise_to_baseline(empty_data, empty_baseline)

    def test_zero_data_raises_error(self):
        """
        Test that an error is raised if the input data consists only of zeros.
        """
        zero_series = pd.Series([0, 0, 0], index=pd.date_range(
            "2024-01-01", periods=3, freq="10min"))
        with self.assertRaises(
                ValueError, msg="Input data consists only of zeros."):
            normalise_to_baseline(zero_series, self.test_data_baseline)

    def test_zero_baseline_raises_error(self):
        """
        Test that an error is raised if the baseline data consists
        only of zeros.
        """
        zero_baseline = pd.Series([0, 0, 0], index=pd.date_range(
            "2024-01-01", periods=3, freq="10min"))
        with self.assertRaises(
                ValueError, msg="Input baseline_data consists only of zeros."):
            normalise_to_baseline(self.test_data, zero_baseline)


class TestLightPhaseActivity(unittest.TestCase):

    def setUp(self):
        # Set up some common data for the tests
        self.data = pd.DataFrame({
            "Activity": [10, 20, 30, 40, 50],
            "Light": [100, 200, 300, 150, 50]
        }, index=pd.date_range(
            start="2023-01-01 00:00:00", periods=5, freq="h"))
        self.empty_data = pd.DataFrame(columns=["Activity", "Light"])
        self.no_light_data = pd.DataFrame({
            "Activity": [10, 20, 30, 40, 50],
            "Light": [100, 100, 100, 100, 100]
        }, index=pd.date_range(
            start="2023-01-01 00:00:00", periods=5, freq="h"))
        self.real_data = generate_test_data(
            days=10, freq="10s", act_night=[0, 1], act_day=[99, 100],
            light_night=[0, 1], light_day=[500, 501])

    def test_valid_data(self):
        # Test normal case
        result = light_phase_activity(self.data, light_col=-1, light_val=150)
        expected = (20 + 30 + 40) / (10 + 20 + 30 + 40 + 50) * 100
        self.assertAlmostEqual(result["Activity"], expected)

    def test_real_data(self):
        # test with generated data
        result = light_phase_activity(
            self.real_data, light_col=-1, light_val=150)
        expected = [100, 100, 50, 100]

        # Use numpy.allclose() for array comparison
        self.assertTrue(np.allclose(np.round(result.values), expected),
                        msg=f"Expected {expected}, but got {result.values}")

    def test_default_parameters(self):
        # Test using default parameters
        result = light_phase_activity(self.data)
        expected = (20 + 30 + 40) / (10 + 20 + 30 + 40 + 50) * 100
        self.assertAlmostEqual(result["Activity"], expected)

    def test_empty_data(self):
        # Test with empty DataFrame
        with self.assertRaises(ValueError):
            result = light_phase_activity(
                self.empty_data, light_col=-1, light_val=150)

    def test_no_light_data(self):
        # Test with no light data exceeding light_val
        result = light_phase_activity(
            self.no_light_data, light_col=-1, light_val=150)
        self.assertEqual(result["Activity"], 0)

    def test_invalid_light_col(self):
        # Test with invalid light_col index
        with self.assertRaises(IndexError):
            light_phase_activity(self.data, light_col=3, light_val=150)

    def test_non_numeric_data(self):
        # Test with non-numeric data in the DataFrame
        data = pd.DataFrame({
            "Activity": [10, 20, 30, 40, 50],
            "Light": ["A", "B", "C", "D", "E"]
        })
        with self.assertRaises(TypeError):
            light_phase_activity(data, light_col=-1, light_val=150)


class TestRelativeAmplitude(unittest.TestCase):

    def setUp(self):
        """Set up test data."""
        # Create a datetime index
        index = pd.date_range("2024-01-01", "2024-01-02", freq="h")

        # Sample data for testing
        self.test_data = pd.DataFrame({
            # Linearly increasing activity
            "Activity1": np.linspace(1, 24, len(index)),
            # Linearly decreasing activity
            "Activity2": np.linspace(24, 1, len(index)),
            "Light": np.random.randint(0, 100, len(index))  # Random activity
        }, index=index)

    def test_linear_increasing_activity(self):
        """Test relative amplitude with linearly increasing activity."""
        result = relative_amplitude(
            self.test_data, active_time=1, inactive_time=1)
        self.assertAlmostEqual(result["Activity1"], 0.92, places=2)

    def test_linear_decreasing_activity(self):
        """Test relative amplitude with linearly decreasing activity."""
        result = relative_amplitude(
            self.test_data, active_time=1, inactive_time=1)
        self.assertAlmostEqual(result["Activity2"], 0.92, places=2)

    def test_random_activity(self):
        """Test relative amplitude with random activity."""
        result = relative_amplitude(
            self.test_data, active_time=5, inactive_time=5)
        self.assertTrue(0 <= result["Light"] <= 1.0)

    def test_single_column(self):
        """Test relative amplitude with a single column."""
        data = self.test_data[["Activity1"]]  # Select only one column
        result = relative_amplitude(data, active_time=1, inactive_time=1)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result["Activity1"], 0.92, places=2)

    def test_non_datetime_index(self):
        """Test that the function raises an error for non-datetime index."""
        data = self.test_data.copy()
        data.reset_index(drop=True, inplace=True)  # Remove the datetime index
        with self.assertRaises(TypeError):
            relative_amplitude(data, active_time=5, inactive_time=5)

    def test_different_time_unit(self):
        """Test relative amplitude with different time units."""
        result = relative_amplitude(
            self.test_data,
            time_unit="2h",
            active_time=2,
            inactive_time=2)
        self.assertTrue("Activity1" in result)
        self.assertTrue("Activity2" in result)
        self.assertTrue("Light" in result)

    def test_edge_case_no_data(self):
        """Test with an empty DataFrame."""
        empty_data = pd.DataFrame(columns=["Activity1", "Activity2", "Light"])
        with self.assertRaises(ValueError):
            result = relative_amplitude(
                empty_data, active_time=5, inactive_time=5)

    def test_edge_case_insufficient_active_inactive_hours(self):
        """Test with fewer rows than active_time + inactive_time."""
        small_data = self.test_data.iloc[:3]  # Subset with only 3 rows
        with self.assertRaises(ValueError):
            result = relative_amplitude(
                small_data, active_time=2, inactive_time=2)


class TestCalculateIS(unittest.TestCase):

    def setUp(self):
        # Generate test data
        self.data = generate_test_data(
            days=10, freq="10s", act_night=[
                0, 10], act_day=[
                10, 100])
        np.random.seed(42)  # Set a seed for reproducibility

    def test_calculate_is_basic(self):
        """Test calculate_IS with valid data."""
        is_value = calculate_IS(self.data, subject_no=0)
        self.assertIsInstance(is_value, float, "The result should be a float.")
        self.assertGreaterEqual(is_value, 0, "IS should be >= 0.")
        self.assertLessEqual(is_value, 1, "IS should be <= 1.")

    def test_calculate_is_different_subjects(self):
        """Test calculate_IS with different subject columns."""
        is_sensor1 = calculate_IS(self.data, subject_no=0)
        is_sensor2 = calculate_IS(self.data, subject_no=1)
        self.assertNotEqual(
            is_sensor1,
            is_sensor2,
            "IS values for different subjects should differ if data differs.")

    def test_calculate_is_empty_data(self):
        """Test calculate_IS with an empty DataFrame."""
        empty_data = pd.DataFrame(columns=["sensor1", "sensor2"])
        with self.assertRaises(
                ValueError,
                msg="Function should raise ValueError for an empty DataFrame."):
            calculate_IS(empty_data, subject_no=0)

    def test_calculate_is_single_row(self):
        """Test calculate_IS with a single row of data."""
        single_row_data = self.data.iloc[:1]
        is_value = calculate_IS(single_row_data, subject_no=0)
        self.assertTrue(
            np.isnan(is_value),
            "IS should be NaN for single-row data due to lack of variance.")

    def test_calculate_is_constant_data(self):
        """Test calculate_IS with constant data."""
        constant_data = generate_test_data(
            days=10,
            freq="10s",
            act_night=[1, 2],
            act_day=[1, 2],
            light_night=[1, 2],
            light_day=[1, 2])

        is_value = calculate_IS(constant_data, subject_no=0)
        self.assertTrue(
            np.isnan(is_value),
            "IS should be NaN for constant data due to zero total variance.")

    def test_calculate_is_invalid_subject(self):
        """Test calculate_IS with an invalid subject index."""
        with self.assertRaises(
                IndexError,
                msg="Function should raise IndexError for"
                    "an invalid subject index."):
            calculate_IS(self.data, subject_no=10)


class TestCalculateTV(unittest.TestCase):

    def setUp(self):
        # Generate test data
        self.data = generate_test_data(
            days=10, freq="10s", act_night=[
                0, 10], act_day=[
                10, 100])
        np.random.seed(42)  # Set a seed for reproducibility

    def test_calculate_tv_basic(self):
        """Test calculate_TV with valid data."""
        tv_value = calculate_TV(self.data, subject_no=0)
        self.assertIsInstance(tv_value, float, "The result should be a float.")
        self.assertGreaterEqual(tv_value, 0, "TV should be >= 0.")
        self.assertLessEqual(tv_value, 1, "TV should be <= 1.")

    def test_calculate_tv_different_subjects(self):
        """Test calculate_TV with different subject columns."""
        tv_sensor1 = calculate_TV(self.data, subject_no=0)
        tv_sensor2 = calculate_TV(self.data, subject_no=1)
        self.assertNotEqual(
            tv_sensor1,
            tv_sensor2,
            "TV values for different subjects should differ if data differs.")

    def test_calculate_tv_empty_data(self):
        """Test calculate_TV with an empty DataFrame."""
        empty_data = pd.DataFrame(columns=["sensor1", "sensor2"])
        with self.assertRaises(
                ValueError,
                msg="Function should raise IndexError for an empty DataFrame."):
            calculate_TV(empty_data, subject_no=0)

    def test_calculate_tv_single_row(self):
        """Test calculate_TV with a single row of data."""
        single_row_data = self.data.iloc[:1]
        tv_value = calculate_TV(single_row_data, subject_no=0)
        self.assertTrue(
            np.isnan(tv_value),
            "TV should be NaN for single-row data due to lack of variance.")

    def test_calculate_tv_constant_data(self):
        """Test calculate_TV with constant data."""
        constant_data = generate_test_data(
            days=10,
            freq="10s",
            act_night=[1, 2],
            act_day=[1, 2],
            light_night=[1, 2],
            light_day=[1, 2])

        tv_value = calculate_TV(constant_data, subject_no=0)
        self.assertTrue(
            np.isnan(tv_value),
            "TV should be NaN for constant data due to zero total variance.")

    def test_calculate_tv_invalid_subject(self):
        """Test calculate_TV with an invalid subject index."""
        with self.assertRaises(IndexError, msg="Function should raise IndexError for an invalid subject index."):
            calculate_TV(self.data, subject_no=10)


if __name__ == "__main_":
    unittest.main()

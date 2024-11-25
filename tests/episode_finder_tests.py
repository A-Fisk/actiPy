import unittest
import sys
import os
import pdb
import numpy as np
import pandas as pd
import datetime
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if True:  # noqa E402
    from actiPy.episodes import find_episodes


class TestFindEpisodes(unittest.TestCase):

    def setUp(self):
        # Generate synthetic test data
        self.index = pd.date_range("2024-01-01", periods=50, freq="10s")
        self.data = pd.DataFrame({
            "Subject 1": [0, 0, 10, 0, 0, 0, 10, 10, 0, 0] * 5,
            "Subject 2": [0, 10, 0, 10, 10, 0, 0, 0, 10, 0] * 5
        }, index=self.index)

        self.expected_index_default = pd.to_datetime([
            "2024-01-01 00:00:20",  # Index 2
            "2024-01-01 00:01:00",  # Index 6-7
            "2024-01-01 00:02:00",  # Index 12
            "2024-01-01 00:02:40",  # Index 16-17
            "2024-01-01 00:03:40",  # Index 22
            "2024-01-01 00:04:20",  # Index 26-27
            "2024-01-01 00:05:20",  # Index 32
            "2024-01-01 00:06:00",  # Index 36-37
            "2024-01-01 00:07:00",  # Index 42
            "2024-01-01 00:07:40"   # Index 46-47
        ])
        self.expected_values_default = [10, 20, 10, 20, 10, 20, 10, 20, 10, 20]

    def test_default_behavior(self):
        # Default min_length="1s" and max_interruption="0s"
        episodes = find_episodes(self.data, subject_no=0)
        expected_values = self.expected_values_default
        expected_index = self.expected_index_default
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_min_length(self):
        # Test with a longer min_length
        episodes = find_episodes(self.data, subject_no=0, min_length="20s")
        expected_index = self.expected_index_default[1::2]
        expected_values = [x for x in self.expected_values_default if x >= 20]
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_max_interruption(self):
        # Test with a max_interruption allowing merging
        episodes = find_episodes(
            self.data,
            subject_no=0,
            max_interruption="30s")
        expected_index = self.expected_index_default[::2]
        expected_values = [
            self.expected_values_default[i] +
            self.expected_values_default[i + 1] + 30
            for i in range(0, len(self.expected_values_default), 2)]
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_min_length_and_max_interruption(self):
        # Test with both min_length and max_interruption
        episodes = find_episodes(
            self.data,
            subject_no=1,
            min_length="20s",
            max_interruption="10s")
        expected_index = self.data.index[2::10]
        expected_values = [40] * 5
        pdb.set_trace()
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_no_valid_episodes(self):
        # Test with no episodes meeting min_length criteria
        episodes = find_episodes(self.data, subject_no=1, min_length="5s")
        self.assertTrue(episodes.empty)

    def test_empty_data(self):
        # Test with empty DataFrame
        empty_data = pd.DataFrame(columns=["Subject 1"], index=self.index)
        episodes = find_episodes(empty_data, subject_no=0)
        self.assertTrue(episodes.empty)

    def test_large_max_interruption(self):
        # Test with a very large max_interruption that merges all episodes
        episodes = find_episodes(
            self.data,
            subject_no=0,
            max_interruption="10s")
        expected_index = pd.to_datetime(["2024-01-01 00:00:00"])
        expected_values = [50]
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )


if __name__ == "__main__":
    unittest.main()

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
        self.index = pd.date_range("2024-01-01", periods=50, freq="1s")
        self.data = pd.DataFrame({
            "Subject 1": [0, 0, 1, 0, 0, 0, 1, 1, 0, 0] * 5,
            "Subject 2": [0, 1, 0, 0, 1, 0, 0, 0, 1, 0] * 5
        }, index=self.index)

    def test_default_behavior(self):
        # Default min_length="1s" and max_interruption="0s"
        episodes = find_episodes(self.data, subject_no=0)
        expected_index = pd.to_datetime(
                ["2024-01-01 00:00:00", 
                 "2024-01-01 00:00:03",
                 "2024-01-01 00:00:08", 
                 "2024-01-01 00:00:13"])
        expected_values = [2, 3, 2, 3]
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_min_length(self):
        # Test with a longer min_length
        episodes = find_episodes(self.data, subject_no=0, min_length="3s")
        expected_index = pd.to_datetime(
            ["2024-01-01 00:00:03", "2024-01-01 00:00:13"])
        expected_values = [3, 3]
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_max_interruption(self):
        # Test with a max_interruption allowing merging
        episodes = find_episodes(
            self.data,
            subject_no=0,
            max_interruption="2s")
        expected_index = pd.to_datetime(
            ["2024-01-01 00:00:00", "2024-01-01 00:00:08"])
        expected_values = [5, 5]
        pd.testing.assert_series_equal(
            episodes, pd.Series(expected_values, index=expected_index),
            check_dtype=False
        )

    def test_min_length_and_max_interruption(self):
        # Test with both min_length and max_interruption
        episodes = find_episodes(
            self.data,
            subject_no=0,
            min_length="3s",
            max_interruption="2s")
        expected_index = pd.to_datetime(
            ["2024-01-01 00:00:00", "2024-01-01 00:00:08"])
        expected_values = [5, 5]
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

# Testing module for sleep analysis

import unittest
import pandas as pd
import actigraphy_analysis.sleep_analysis as sleep_analysis

# test sleep processing


class testSleepProcessing(unittest.TestCase):

    def setUp(self):
        # generate data for sleep processing
        # list of 100's with known number of 4x0s

        high_no_list = [100 for x in range(100)]

        self.test_data_series = pd.Series(high_no_list)

        self.test_data_series[10:14] = 0

        self.test_data_series[57:61] = 0

        self.test_data_series[82:86] = 0

    def test_sleep_processing(self):
        # test whether picks up correct number of sleep episodes

        sleep_scored_data = sleep_analysis.sleep_process(self.test_data_series)

        sleep_scored_sum = sleep_scored_data.sum()

        self.assertEqual(3, sleep_scored_sum)

if __name__ == "__main__":
    unittest.main()



# TODO Implement tests for following functions:
# TODO sleep create df
# TODO create_hourly_sum
# TODO simple_plot

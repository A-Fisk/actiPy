# Testing module for sleep analysis

import unittest
import pandas as pd
import actiPy.sleep_process as sleep
import actiPy.episodes as ep

# test sleep processing

class testSleepProcessing(unittest.TestCase):

    def setUp(self):
        # generate data for sleep processing
        # list of 100's with known number of 4x0s
        high_no_list = [100 for x in range(400)]
        index = pd.DatetimeIndex(start='2018-01-01',
                                 freq='10s',
                                 periods=len(high_no_list))
        self.test_data_series = pd.Series(high_no_list,
                                          index=index)
        self.test_data_series[10:14] = 0
        self.test_data_series[57:61] = 0
        self.test_data_series[82:86] = 0
        self.test_data_series[100:200] = 0
        self.test_data_series[201:204] = 10
        self.sleep_scored_data = sleep.sleep_process(
            self.test_data_series)
        
    def test_sleep_processing(self):
        # test whether picks up correct number of sleep episodes
        # by finding total score of sleep
        sleep_scored_sum = self.sleep_scored_data.sum()
        self.assertEqual(100, sleep_scored_sum)

    def test_sleep_episodes(self):
        # test if correct number of sleep episodes from ep
        # finder function
        episodes = ep.episode_finder(self.sleep_scored_data)
        no_episodes = len(episodes)
        self.assertEqual(no_episodes,4)
        
if __name__ == "__main__":
    unittest.main()



# TODO Implement tests for following functions:
# TODO sleep create df


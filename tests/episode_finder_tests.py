# Tests for episode finder scripts

import unittest
import numpy as np
import pandas as pd
import actiPy.episode_finder as ep

np.random.seed(42)

class test_episode_finder(unittest.TestCase):
    """
    Class to test functionality of episode finder.
    Needs to be able to handle 000 - check it rejects
    if there are no non0 numbers present
    """
    def setUp(self):
        # create a test dataframe with a set
        # number of episodes in it and with a 000
        # string in there too
        random_segment = np.random.randint(1,100, 20)
        rand_seg_withzero = np.append(random_segment, 0)
        multiple_episodes = [rand_seg_withzero for x in range(10)]
        concat_array = np.concatenate(multiple_episodes)
        trip_zero_seg = np.append(random_segment, np.zeros(3))
        final_few_episodes = [rand_seg_withzero,
                              trip_zero_seg,
                              rand_seg_withzero]
        final_ep_concat = np.concatenate(final_few_episodes)
        final_episode_array = np.append(concat_array, final_ep_concat)
        
        # create index for array
        index = pd.DatetimeIndex(start='2018-01-01',
                                 freq="10S",
                                 periods=len(final_episode_array))
        episode_series = pd.Series(data=final_episode_array,
                                   index=index)
        self.episode_data = episode_series
        
    def test_episode_finder(self):
        # check it finds the right number of episodes
        # calc as 12?
        episodes = ep.episode_finder(self.episode_data)
        self.assertEqual(len(episodes), 12)
    
if __name__ == "__main__":
    unittest.main()
    
    
    
    
# TODO pipe dream create test for different base_times
# only useful once in production mode

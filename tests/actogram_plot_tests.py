import unittest
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "/Users/angusfisk/Documents/01_PhD_files/"
                   "07_python_package/actiPy")
import actiPy.preprocessing as prep
import actiPy.actogram_plot as act

# developing actogram scripting

np.random.seed(42)

class tests_actogram_plot_support_functions(unittest.TestCase):
    """
    test for peripheral functions for actogram plot
    """
    def setUp(self):
        # create two days of data
        day_one = np.random.randint(0,100,100)
        day_two = np.random.randint(0,100, 100)
        day_three = np.zeros(100)
        data = pd.DataFrame({"1":day_one,
                             "2":day_two,
                             "3":day_three})
        self.test_data = data
        
    def test_pad_first_last_day(self):
        data_padded = act.pad_first_last_days(self.test_data)
        no_days = len(data_padded.columns)
        self.assertEqual(no_days, 5)
        
    def test_convert_zeros(self):
        # check whether any zeros are left
        data_nozero = act.convert_zeros(self.test_data, 10)
        check_zeros = ((data_nozero == 0).any()).any()
        self.assertFalse(check_zeros)

    def test_get_two_days_as_array(self):
        # get first two days and check length of df
        length_day = len(self.test_data.iloc[:,0])
        length_two_days = length_day + len(self.test_data.iloc[:,1])
        day_one_label = self.test_data.columns[0]
        two_days = act.get_two_days_as_array(self.test_data,
                                             day_one_label)
        self.assertEqual(len(two_days), length_two_days)
        
if __name__ == "main":
    unittest.main()

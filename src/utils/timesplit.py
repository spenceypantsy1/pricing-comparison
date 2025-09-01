"""
In this module, we define 2 simple splits for time series data:

1. Expanding Split: A single split that continually adds to the training set while keeping testing size fixed
    - This is useful for simulating a real-time forecasting scenario with traditional financial models
    - Traditional financial models rely heavily on statistical properties over time
    * alternatively we can use timeseries split from sklearn.model_selection

2. Rolling Split: Multiple splits that simulate a rolling forecast origin, useful for backtesting
    - This is useful for machine learning models that can be retrained frequently
    - Machine learning models can adapt to new data patterns more flexibly
"""

import numpy as np
from sklearn.model_selection import TimeSeriesSplit

class ExpandingSplit:
    def __init__(self, test_size = 1, step_size = 1):
        self.test_size = test_size                      # test size (int) = number of samples in the test set per split
        self.step_size = step_size                      # step size (int) = how much to move forward split each iteration

    def split(self, data):
        n =  len(data)
        print("Total samples:", n)

        start = 0
        end = n - self.test_size
        
        for test_start in range(start, end, self.step_size):
            train_idx = np.arange(0, test_start + 1)
            test_idx = np.arange(test_start + 1, test_start + 1 + self.test_size)
            if test_idx[-1] < n:
                yield train_idx, test_idx
            print("Train indices:", train_idx, "Test indices:", test_idx)


class RollingSplit:
    def __init__(self, train_size, test_size, step_size = 1):
        self.train_size = train_size                    # train size (int) = number of samples in the training set per split
        self.test_size = test_size                      # test size (int) = number of samples in the test set per split
        self.step_size = step_size                      # step size (int) = how much to move forward split each iteration

    def split(self, data):
        n =  len(data)
        print("Total samples:", n)

        start = 0 

        while start + self.train_size + self.test_size <= n:
            train_idx = np.arange(start, start + self.train_size)
            test_idx = np.arange(start + self.train_size, start + self.train_size + self.test_size)
            yield train_idx, test_idx
            start += self.step_size             # move start forward by stepsize until we reach <= n as above
            print("Train indices:", train_idx, "Test indices:", test_idx)




"""
Total samples: 10
----------------------------------------
Rolling Split - Train: [0 1 2] Test: [3 4]
Train indices: [0 1 2] Test indices: [3 4]
----------------------------------------
Rolling Split - Train: [2 3 4] Test: [5 6]
Train indices: [2 3 4] Test indices: [5 6]
----------------------------------------
Rolling Split - Train: [4 5 6] Test: [7 8]
Train indices: [4 5 6] Test indices: [7 8]
========================================
Total samples: 10
----------------------------------------
Expanding Split - Train: [0] Test: [1 2]
Train indices: [0] Test indices: [1 2]
----------------------------------------
Expanding Split - Train: [0 1 2] Test: [3 4]
Train indices: [0 1 2] Test indices: [3 4]
----------------------------------------
Expanding Split - Train: [0 1 2 3 4] Test: [5 6]
Train indices: [0 1 2 3 4] Test indices: [5 6]
----------------------------------------
Expanding Split - Train: [0 1 2 3 4 5 6] Test: [7 8]
Train indices: [0 1 2 3 4 5 6] Test indices: [7 8]
"""
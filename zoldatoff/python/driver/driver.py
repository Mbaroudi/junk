#!/usr/bin/env python
#coding: utf-8

"""
Driver Telematics Analysis
==========================

https://www.kaggle.com/c/axa-driver-telematics-analysis

AXA has provided a dataset of over 50,000 anonymized driver trips.
The intent of this competition is to develop an algorithmic signature
of driving type.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
SHIFT_LEN = 3
BINS_NUM = 20

VELOCITY_LOW = 1
VELOCITY_HIGH = 15
ACCEL_MINLEN = 15

DRIVER_NUM = 1
NUM_CSV = 10



def csv2dataframe(filename=DATA_PATH + '/1/1.csv'):
    """
    Function extracts data from csv file and enriches it with velocity and acceleration data
    """

    data = pd.DataFrame.from_csv(filename, index_col=False)

    # pylint: disable=E1103
    data['t'] = data.index
    data['dt'] = data['t'] - data['t'].shift(SHIFT_LEN)
    data['ds'] = sum([
        np.sqrt(
            np.square(data['x'] - data['x'].shift(shift+1))
            +
            np.square(data['y'] - data['y'].shift(shift+1))
        )
        for shift in range(SHIFT_LEN)
    ])
    data['v'] = data['ds'] / data['dt']
    data['a'] = (data['v'] - data['v'].shift(SHIFT_LEN)) / data['dt']
    # pylint: enable=E1103

    return data




def extract_accel(data):
    """
    Function searches for acceleration parts of trajectory
    """

    accel_all = []
    accel = []

    row_iterator = data.iterrows()
    prev = row_iterator.next()

    for i, curr in row_iterator:

        if len(accel) == 0 and VELOCITY_LOW < curr['v'] < VELOCITY_HIGH:
            accel.append((i, curr['v']))

        elif len(accel) > 0 and VELOCITY_LOW < curr['v'] and (curr['a'] > 0.0 or prev['a'] > 0.0):
            accel.append((i, curr['v']))

        elif len(accel) > ACCEL_MINLEN and curr['a'] < 0.0 and prev['a'] < 0.0:
            accel_all.append(pd.DataFrame(accel, columns=['t', 'v']))
            accel = []

        else:
            accel = []

        prev = curr

    return accel_all





def plot_driver():
    """
    Takes several files, extracts acceleration parts of trajectories
    and makes a plot of them
    """

    fig = plt.figure()

    for i in range(NUM_CSV):
        driver_data = csv2dataframe(DATA_PATH + '/' + str(DRIVER_NUM) + '/' + str(i+1) + '.csv')

        accel_all = extract_accel(driver_data)

        for accel in accel_all:
            accel['v'].plot(ax=fig.gca())

        print 'driver =', DRIVER_NUM, 'traj =', i, ' accel_cnt = ', len(accel_all)

    plt.autoscale()
    plt.legend(ncol=3, loc='lower right', fontsize=7)
    plt.savefig('behavior.eps')


plot_driver()

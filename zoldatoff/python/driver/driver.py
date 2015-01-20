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

# Откуда и сколко траекторий берём
DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
DRIVER_NUM = 10
NUM_CSV = 10


SHIFT_LEN = 1       # Усреднение по SHIFT_LEN точкам при расчёте скоорости
VELOCITY_LOW = 1    # Участок ускорения отбирается для скоростей из диапазона
VELOCITY_HIGH = 15  # между VELOCITY_LOW и VELOCITY_HIGH
ACCEL_MINLEN = 15   # Длина участка разгона не менее ACCEL_MINLEN точек



def csv2dataframe(filename=DATA_PATH + '/1/1.csv'):
    """
    Function extracts data from csv file and enriches it with velocity and acceleration data
    """

    data = pd.DataFrame.from_csv(filename, index_col=False)

    # pylint: disable=E1103
    data['t'] = data.index                                              # время
    data['dt'] = data['t'] - data['t'].shift(SHIFT_LEN)                 # дельта времени
    data['ds'] = sum([                                                  # расстояние
        np.sqrt(
            np.square(data['x'].shift(shift) - data['x'].shift(shift+1))
            +
            np.square(data['y'].shift(shift) - data['y'].shift(shift+1))
        )
        for shift in range(SHIFT_LEN)
    ])
    data['v'] = data['ds'] / data['dt']                                 # скорость
    data['a'] = (data['v'] - data['v'].shift(SHIFT_LEN)) / data['dt']   # ускорение
    data['ang'] = np.where(                                             # направление движения
        data['ds'] > 0.0,
        np.arctan2(
            data['y']-data['y'].shift(1),
            data['x']-data['x'].shift(1)
        ),
        0.0
    )
    data['dang'] = data['ang'] - data['ang'].shift(1)                   # смена направления движения
    data['r'] = data['ds'] / (abs(data['dang']) + 0.000001)             # радиус поворота
    # pylint: enable=E1103

    #print data[['x', 'y', 'ang']]

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
            accel.append((i, curr['v'], curr['a']))

        elif len(accel) > 0 and VELOCITY_LOW < curr['v'] and (curr['a'] > 0.0 or prev['a'] > 0.0):
            accel.append((i, curr['v'], curr['a']))

        elif len(accel) > ACCEL_MINLEN and curr['a'] < 0.0 and prev['a'] < 0.0:
            accel_all.append(pd.DataFrame(accel, columns=['t', 'v', 'a']))
            accel = []

        else:
            accel = []

        prev = curr

    return accel_all




def plot_stats():
    """
    Make plots as in this article: http://cs229.stanford.edu/proj2013/DriverIdentification.pdf
    'Driver Identification by Driving Style'
    """

    for i in range(NUM_CSV):
        driver_data = csv2dataframe(DATA_PATH + '/' + str(DRIVER_NUM) + '/' + str(i+1) + '.csv')

        accel_all = extract_accel(driver_data)

        for accel in accel_all:
            plt.figure(4)
            accel['v'].plot()

            plt.figure(5)
            accel['a'].hist(bins=80, normed=True)


        fig = plt.figure(1)
        driver_data.plot(x='x', y='y', ls='--', ax=fig.gca()) #color='red', markerfacecolor='red',

        plt.figure(2)
        driver_data['v'].hist(bins=40, range=(1, 41), normed=True)

        plt.figure(3)
        driver_data['a'].hist(bins=40, range=(0.1, 5.0), normed=True)

        fig = plt.figure(6)
        driver_data.plot(x='r', y='v', ls='', marker='.', ax=fig.gca())

        fig = plt.figure(7)
        driver_data.plot(x='t', y='ang', ax=fig.gca())

        print 'driver =', DRIVER_NUM, 'traj =', i, ' accel_cnt = ', len(accel_all)

    plt.figure(1)
    plt.autoscale()
    #plt.legend().remove() #(ncol=3, loc='lower right', fontsize=7)
    plt.savefig('trajectory.eps')

    plt.figure(2)
    plt.savefig('velocity.eps')

    plt.figure(3)
    plt.savefig('acceleration.eps')

    plt.figure(4)
    plt.savefig('accel_v.eps')

    plt.figure(5)
    plt.xlim([0.01, 4.0])
    plt.savefig('accel_a.eps')

    plt.figure(6)
    plt.autoscale()
    plt.xlim([0.01, 10.0])
    plt.ylim([0.01, 10.0])
    plt.savefig('r_v.eps')

    plt.figure(7)
    plt.autoscale()
    plt.xlim([0.01, 110.0])
    plt.savefig('angle.eps')


plot_stats()

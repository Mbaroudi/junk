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

import os
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Откуда и сколко траекторий берём
DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
DRIVER_NUM = 1
NUM_CSV = 30

VELOCITY_LOW = 5    # Участок ускорения отбирается для скоростей из диапазона
VELOCITY_HIGH = 15  #       между VELOCITY_LOW и VELOCITY_HIGH
ACCEL_MINLEN = 15   # Длина участка разгона не менее ACCEL_MINLEN точек
#ACCEL_HEAD = 5     # В начале разгона ускорение завышено - этот участок мы отбрасываем
ACCEL_TAIL = 3      # В конце разгона ускорение снижается - этот участок мы отбрасываем



def csv2dataframe(filename=DATA_PATH + '/1/1.csv'):
    """
    Function extracts data from csv file and enriches it with velocity and acceleration data
    """

    data = pd.DataFrame.from_csv(filename, index_col=False)

    # pylint: disable=E1103
    data['t'] = data.index                                              # время
    data['dt'] = data['t'] - data['t'].shift(1)                         # дельта времени
    data['ds'] = np.sqrt(                                               # расстояние
        np.square(data['x'] - data['x'].shift(1))
        +
        np.square(data['y'] - data['y'].shift(1))
    )
    data['v'] = data['ds'] / data['dt']                                 # скорость
    data['a'] = (data['v'] - data['v'].shift(1)) / data['dt']           # ускорение
    data['ang'] = np.where(                                             # направление движения
        data['ds'] > 0.5,
        np.arctan2(
            data['y']-data['y'].shift(1),
            data['x']-data['x'].shift(1)
        ),
        None
    )

    data['dang'] = data['ang'] - data['ang'].shift(1)                   # смена направления движения
    data['dang'] = data['dang'].apply(lambda x: x - 2.0*np.pi if x >  4.0 else x)
    data['dang'] = data['dang'].apply(lambda x: x + 2.0*np.pi if x < -4.0 else x)

    data['r'] = (data['ds'] + data['ds'].shift(1)) / (abs(data['dang']) + 0.000001)             # радиус поворота
    # pylint: enable=E1103

    #print data[['x', 'y', 'ds', 'v', 'ang', 'dang', 'r']]

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
            df = pd.DataFrame(accel, columns=['t', 'v', 'a'])
            accel_all.append(df[0:-ACCEL_TAIL])
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

    path = DATA_PATH + '/' + str(DRIVER_NUM) + '/'
    files = os.listdir(path)

    for file in random.sample(files, NUM_CSV):
        driver_data = csv2dataframe(path + file)

        accel_all = extract_accel(driver_data)

        accel_a = []

        for accel in accel_all:
            plt.figure(4)
            accel['v'].plot()

            accel_a.append(accel['a'].mean())

        plt.figure(5)
        if accel_a:
            plt.hist(accel_a, range=(0, 5), bins=40, normed=True)

        fig = plt.figure(1)
        driver_data.plot(x='x', y='y', ls='--', ax=fig.gca()) #color='red', markerfacecolor='red',

        plt.figure(2)
        driver_data['v'].hist(bins=40, normed=True)

        plt.figure(3)
        driver_data['a'].hist(bins=40, normed=True)

        fig = plt.figure(6)
        driver_data.plot(x='r', y='v', ls='', marker='.', ax=fig.gca())

        #fig = plt.figure(7)
        #driver_data.plot(x='t', y='ang', ax=fig.gca())

        fig = plt.figure(8)
        driver_data.plot(x='t', y='v', ax=fig.gca())

        print 'driver =', DRIVER_NUM, 'file =', file, ' accel_cnt = ', len(accel_all)

    plt.figure(1)
    plt.autoscale()
    plt.legend().remove() #(ncol=3, loc='lower right', fontsize=7)
    plt.savefig(str(DRIVER_NUM) + '. trajectory.eps')

    plt.figure(2)
    plt.xlim([1, 45])
    plt.ylim([0, 0.5])
    plt.savefig(str(DRIVER_NUM) + '. v(hist).eps')

    plt.figure(3)
    plt.xlim([0.2, 6])
    plt.ylim([0, 1])
    plt.savefig(str(DRIVER_NUM) + '. a(hist).eps')

    plt.figure(4)
    plt.xlim([0, 45])
    plt.ylim([0, 30])
    plt.savefig(str(DRIVER_NUM) + '. accel v(t).eps')

    plt.figure(5)
    plt.xlim([0.01, 4])
    plt.ylim([0, 10])
    plt.savefig(str(DRIVER_NUM) + '. accel mean(a).eps')

    plt.figure(6)
    plt.legend().remove()
    plt.xlim([0, 10])
    plt.ylim([0, 10])
    plt.savefig(str(DRIVER_NUM) + '. v(r).eps')

    #plt.figure(7)
    #plt.legend().remove()
    #plt.xlim([0, 50])
    #plt.ylim([-4, 4])
    #plt.savefig(str(DRIVER_NUM) + '. ang(t).eps')

    plt.figure(8)
    plt.legend().remove()
    plt.xlim([0, 500])
    plt.ylim([0, 30])
    plt.savefig(str(DRIVER_NUM) + '. v(t).eps')


plot_stats()

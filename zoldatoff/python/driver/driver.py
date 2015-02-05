#!/usr/bin/env python
# coding: utf-8

"""
Driver Telematics Analysis
==========================

https://www.kaggle.com/c/axa-driver-telematics-analysis

AXA has provided a dataset of over 50,000 anonymized driver trips.
The intent of this competition is to develop an algorithmic signature
of driving type.
"""

# import os
# import random

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
# import matplotlib.font_manager as fm
import seaborn as sns

# import scipy.cluster.hierarchy as hac
# import scipy.spatial.distance as dis

# from collections import Counter
# from pykalman import KalmanFilter

# Откуда и сколько траекторий берём
DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
PLOT_EXT = '.png'


class Trip(object):
    """
    This class:
     * reads trip data from csv file
    """

    def __init__(self, driver_num=1, trip_num=1):
        print 'Driver = ' + str(driver_num) + ', trip = ' + str(trip_num)

        self.driver_num = driver_num
        self.trip_num = trip_num
        self.driver_trip = str(int(driver_num)) + '_' + str(int(trip_num))

        self.get_data()
        self.set_flags()

        self.plot_data()
        self.plot_trip()
        self.plot_rv()

        # print self.trip_data[self.trip_data.t < 30]

    # =========================================================================
    def get_data(self):
        """
        Reads trip data (x, y) from csv file
        """
        trip_filename = str(self.trip_num) + '.csv'
        trip_path = DRIVER_PATH + '/' + str(self.driver_num) + '/'
        self.trip_data = pd.DataFrame.from_csv(
            trip_path + trip_filename, index_col=False)
        # self.trip_data.columns = ['_x_', '_y_']
        self.trip_data.columns = ['x', 'y']

        self.trip_data['t'] = self.trip_data.index
        # self.trip_data[['x', 'y'] = self.trip_data[['_x_', '_y_']
        self.trip_data['v'] = self.distance(self.trip_data, 'x', 'y')
        self.trip_data['a'] = self.trip_data.v.diff()
        self.trip_data['r'] = self.radius(self.trip_data, 'x', 'y')
        self.trip_data['ang'] = self.angle(self.trip_data, 'x', 'y')

    # =========================================================================
    def plot_data(self):
        """
        Draws a plot of trip data
        """

        df = self.trip_data

        fig, axes = plt.subplots(2, 2)

        df[df.flag_accel == 1].plot(
            x='t', y='v', ax=axes[0, 0], ls='', marker='.', color='r')
        df[df.flag_decel == 1].plot(
            x='t', y='v', ax=axes[0, 0], ls='', marker='.', color='g')
        df[df.flag_accel + df.flag_decel == 0].plot(
            x='t', y='v', ax=axes[0, 0], ls='', marker='.', color='k')
        axes[0, 0].set_title('Velocity')
        axes[0, 0].legend().remove()
        # axes[0, 0].set_xlim([200, 400])

        df[df.flag_accel == 1].plot(
            x='t', y='a', ax=axes[0, 1], ls='', marker='.', color='r')
        df[df.flag_decel == 1].plot(
            x='t', y='a', ax=axes[0, 1], ls='', marker='.', color='g')
        df[df.flag_accel + df.flag_decel == 0].plot(
            x='t', y='a', ax=axes[0, 1], ls='', marker='.', color='k')
        axes[0, 1].set_title('Acceleration')
        axes[0, 1].legend().remove()
        # axes[0, 1].set_xlim([200, 400])

        df[df.flag_turn == 1].plot(
            x='t', y='r', ax=axes[1, 0], ls='', marker='.', color='r')
        # df[df.flag_turn == 0].plot(x='t', y='r', ax=axes[1, 0], color='k')
        axes[1, 0].set_title('Radius')
        axes[1, 0].legend().remove()
        axes[1, 0].autoscale()
        # axes[1, 0].set_xlim([200, 400])
        # axes[1, 0].set_ylim([0, 2000])

        df[df.flag_turn == 1].plot(
            x='t', y='ang', ax=axes[1, 1], ls='', marker='.', color='r')
        # df[df.flag_turn == 0].plot(x='t', y='ang', ax=axes[1, 1], color='k')
        axes[1, 1].set_title('Angle')
        axes[1, 1].legend().remove()
        axes[1, 0].autoscale()
        # axes[1, 1].set_xlim([200, 400])

        sns.despine()
        fig.savefig(self.driver_trip + '_data' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_trip(self):
        """
        Makes an x-y plot
        """

        df = self.trip_data
        fig, axes = plt.subplots()

        df.plot(x='x', y='y', ax=axes)

        axes.autoscale()
        plt.axis('equal')
        axes.legend().remove()
        sns.despine()
        fig.savefig(self.driver_trip + '_trip' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_rv(self):
        """
        Makes an x-y plot
        """

        df = self.trip_data
        fig, axes = plt.subplots()

        df[df.flag_turn == 1].plot(x='r', y='v', ax=axes, ls='', marker='.')

        axes.set_xlim([0, 40])
        axes.legend().remove()
        sns.despine()
        fig.savefig(self.driver_trip + '_rv' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def set_flags(self):
        """
        Sets flags for special parts of trip
        """

        df = self.trip_data

        n = 5
        df['flag_accel'] = \
            pd.rolling_sum(df.a.apply(lambda x: 1 if x > 0 else 0), n) \
            .apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

        df['flag_decel'] = \
            pd.rolling_sum(df.a.apply(lambda x: 1 if x < 0 else 0), n) \
            .apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

        df['flag_turn'] = \
            pd.rolling_sum(
                df.apply(lambda x: 1 if x.r < 100 and x.v > 2 else 0, axis=1),
                n
            ).apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

    @staticmethod
    def distance(df, x, y):
        return np.sqrt(df.x.diff()**2 + df.y.diff()**2)

    @staticmethod
    def radius(df, x, y):
        x1, y1 = df.x.shift(-1), df.y.shift(-1)
        x2, y2 = df.x, df.y
        x3, y3 = df.x.shift(1), df.y.shift(1)

        a = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        b = np.sqrt((x3-x2)**2 + (y3-y2)**2)
        c = np.sqrt((x3-x1)**2 + (y3-y1)**2)

        s = (a + b + c) / 2.0
        R = a * b * c / 4.0 / np.sqrt(s * (s - a) * (s - b) * (s - c))
        return R

    @staticmethod
    def angle(df, x, y):
        x1, y1 = df.x.shift(-1), df.y.shift(-1)
        x2, y2 = df.x, df.y
        x3, y3 = df.x.shift(1), df.y.shift(1)

        a = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        b = np.sqrt((x3-x2)**2 + (y3-y2)**2)
        c = np.sqrt((x3-x1)**2 + (y3-y1)**2)

        return np.arccos((a**2 + c**2 - b**2) / (2.0 * a * c))

tr = Trip(driver_num=2)

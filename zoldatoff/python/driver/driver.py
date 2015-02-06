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

import os
import random

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# import seaborn as sns

import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as dis

from collections import Counter
# from pykalman import KalmanFilter

# Откуда и сколько траекторий берём
DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
PLOT_EXT = '.eps'
NUM_TRIP = 10
METHOD = 'single'

COLORS = [
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E']


# =============================================================================
# =============================================================================
# =============================================================================
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
        self.get_kpi()

        # self.plot_data()
        # self.plot_trip()
        # self.plot_rv()

        # print self.kpi
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

        n = 3

        df_turn = df.apply(lambda x: 1
                           if x.r < 80 and x.v > 2 and x.ang > 0.05
                           else 0,
                           axis=1)
        df['flag_turn_left'] = pd.rolling_sum(df_turn, n) \
            .apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

        df_turn = df.apply(lambda x: 1
                           if x.r < 80 and x.v > 2 and x.ang < -0.05
                           else 0,
                           axis=1)
        df['flag_turn_right'] = pd.rolling_sum(df_turn, n) \
            .apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

    # =========================================================================
    def get_kpi(self):
        df = self.trip_data
        kpi = pd.Series(None)

        kpi['driver_trip'] = self.driver_trip
        kpi['driver_num'] = self.driver_num
        kpi['trip_num'] = self.trip_num

        df_turn = df[(df.flag_turn_left == 1) | (df.flag_turn_right == 1)]
        kpi['vR'] = df_turn[df_turn.r <= 70].v.max()

        kpi['a'] = df[df.flag_accel == 1].a.max()

        self.kpi = kpi

    # =========================================================================
    def plot_data(self):
        """
        Draws a plot of trip data
        """

        df = self.trip_data

        fig, axes = plt.subplots(2, 2)

        # Velocity
        ax = axes[0, 0]
        df.plot(x='t', y='v', ax=ax, ls='--', color='gray')

        dfp = df[df.flag_accel == 1]
        if not dfp.empty:
            df[df.flag_accel == 1].plot(x='t', y='v', ax=ax,
                                        ls='', marker='.', color='r')

        dfp = df[df.flag_decel == 1]
        if not dfp.empty:
            df[df.flag_decel == 1].plot(x='t', y='v', ax=ax,
                                        ls='', marker='.', color='g')

        ax.set_ylabel('Velocity')
        ax.legend(['', 'acceleration', 'deceleration'])
        ax.set_xlabel('time (s)')

        # Acceleration
        ax = axes[0, 1]
        df.plot(x='t', y='a', ax=ax, ls='--', color='gray')
        df[df.flag_accel == 1].plot(x='t', y='a', ax=ax,
                                    ls='', marker='.', color='r')
        df[df.flag_decel == 1].plot(x='t', y='a', ax=ax,
                                    ls='', marker='.', color='g')
        ax.set_ylabel('Acceleration')
        ax.legend(['', 'acceleration', 'deceleration'], loc='upper left')
        ax.set_xlabel('time (s)')
        ax.set_ylim([-3, 3])

        # Radius
        ax = axes[1, 0]
        # df.plot(x='t', y='r', ax=axes[1], ls='--', color='k')
        df[df.flag_turn_left == 1].plot(x='t', y='r', ax=ax,
                                        ls='', marker='.', color='r')
        df[df.flag_turn_right == 1].plot(x='t', y='r', ax=ax,
                                         ls='', marker='.', color='b')
        ax.set_ylabel('Radius')
        ax.legend(['left', 'right'], loc='upper right')
        ax.set_xlabel('time (s)')
        ax.set_ylim([0, 100])
        ax.set_xbound(lower=0.0, upper=df.t.max())

        # Angle
        ax = axes[1, 1]
        # df.plot(x='t', y='ang', ax=ax2, ls='--', color='k')
        df[df.flag_turn_left == 1].plot(x='t', y='ang', ax=ax,
                                        ls='', marker='.', color='r')
        df[df.flag_turn_right == 1].plot(x='t', y='ang', ax=ax,
                                         ls='', marker='.', color='b')
        ax.set_ylabel('Angle')
        ax.legend(['left', 'right'], loc='upper left')
        ax.set_xlabel('time (s)')
        ax.set_ylim([-0.5, 0.5])
        ax.set_xbound(lower=0.0, upper=df.t.max())

        # sns.despine()

        fig.set_size_inches(15, 10)
        fig.savefig(self.driver_trip + '_data' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_trip(self):
        """
        Makes an x-y plot
        """

        df = self.trip_data
        fig, axes = plt.subplots()

        df.plot(x='x', y='y', ax=axes, color='gray')
        df[df.flag_turn_left == 1].plot(x='x', y='y', ax=axes, color='r',
                                        ls='', marker='.')
        df[df.flag_turn_right == 1].plot(x='x', y='y', ax=axes, color='b',
                                         ls='', marker='.')
        df[df.index <= 10].plot(x='x', y='y', ax=axes, color='r',
                                         ls='', marker='x')
        axes.legend(['', 'left', 'right'])

        axes.autoscale()
        plt.axis('equal')

        fig.savefig(self.driver_trip + '_trip' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_rv(self):
        """
        Makes an x-y plot
        """

        df = self.trip_data
        fig, axes = plt.subplots()

        df[df.flag_turn_left == 1].plot(
            x='r', y='v', ax=axes, ls='', marker='.', color='g')
        df[df.flag_turn_right == 1].plot(
            x='r', y='v', ax=axes, ls='', marker='.', color='b')

        axes.set_xlim([0, 100])
        axes.legend().remove()
        # sns.despine()
        fig.savefig(self.driver_trip + '_rv' + PLOT_EXT)
        plt.close(fig)

    # ------------------------------------------------------------------
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
        x1, y1 = df.x.shift(1), df.y.shift(1)
        x2, y2 = df.x, df.y
        x3, y3 = df.x.shift(-1), df.y.shift(-1)

        a1 = np.arctan2(y2-y1, x2-x1)
        a2 = np.arctan2(y3-y2, x3-x2)
        ang = a2 - a1

        np.where(ang > np.pi, ang - 2.0*np.pi, ang)
        np.where(ang < -np.pi, ang + 2.0*np.pi, ang)

        return ang


# =============================================================================
# =============================================================================
class Driver(object):
    """
    Driver is a class that contains:
     * trips data
     * method for clustering KPI's
     * methods for data visualization
    """
    # @profile
    def __init__(self, driver_num=1, method='csv'):
        """
        Loads trip (or KPI) data from files
        """
        self.driver_num = driver_num

        if method == 'csv':
            self.get_data()
            self.cluster()
            self.save_kpi()
            self.plot_rv()

        else:
            self.load_kpi()

        self.plot_kpi()
        print self.kpis

    # =========================================================================
    def get_data(self):
        self.trips = []
        self.kpis = pd.DataFrame(None)

        trip_file_path = DRIVER_PATH + '/' + str(self.driver_num) + '/'
        files = os.listdir(trip_file_path)

        # for file_name in random.sample(files, NUM_TRIP):
        for file_name in files:
            trip_num = int(os.path.splitext(file_name)[0])
            trip = Trip(self.driver_num, trip_num)
            self.trips.append(trip)
            self.kpis = self.kpis.append(trip.kpi, ignore_index=True)

        self.kpis.sort(['driver_num', 'trip_num'], inplace=True)

    # =========================================================================
    def save_kpi(self):
        """
        Saves KPI data to disk
        """
        self.kpis.to_csv(str(self.driver_num) + '.txt', index=False)

    # =========================================================================
    def load_kpi(self):
        """
        Loads KPI data from disk
        """
        file_fullname = str(self.driver_num) + '.txt'
        self.kpis = pd.DataFrame.from_csv(file_fullname, index_col=False)

    # =========================================================================
    @staticmethod
    def normalize(df, column):
        df_min, df_max = df[column].min(), df[column].max()
        if df_min == df_max:
            df[column] = 0.5,
        else:
            df[column] -= df_min
            df[column] /= df_max - df_min

        return df

    # =========================================================================
    def cluster(self):
        """
        Scales and clusters KPI data
        http://stackoverflow.com/questions/21638130/tutorial-for-scipy-cluster-hierarchy
        """

        columns = ['vR', 'a']
        kpis = self.kpis[columns].copy()
        for column in columns:
            self.normalize(kpis, column)
            kpis[column].fillna(0.5, inplace=True)

        matr = kpis.as_matrix(columns=columns)
        a = dis.squareform(dis.pdist(matr))
        z = hac.linkage(a, method=METHOD)
        knee = np.diff(z[::-1, 2], 2)
        # num_clust = knee.argmax() + 2
        # knee[knee.argmax()] = 0
        # num_clust = knee.argmax() + 2
        num_clust = 5
        part = hac.fcluster(z, num_clust, 'maxclust')

        mc = Counter(part).most_common(1)[0][0]
        self.kpis['prob'] = [1 if p == mc else 0 for p in part.tolist()]

        self.plot_cluster(a, z, knee, num_clust, part)

    # =========================================================================
    def plot_cluster(self, a, z, knee, num_clust, part):
        """
        Makes a plot of clustering result
        """
        print 'Plotting cluster'

        fig, axes = plt.subplots(1, 3)

        # Plot #1
        axes[0].plot(range(1, len(z)+1), z[::-1, 2])
        axes[0].plot(range(2, len(z)), knee)
        axes[0].grid()

        font = fm.FontProperties()
        font.set_family('Consolas')
        axes[0].text(
            num_clust,
            z[::-1, 2][num_clust-1],
            'possible\n<- knee point',
            fontproperties=font)

        # Plot #2
        # Раскраска по тестовым кластерам
        part = [1 for i in range(1, 21)] \
            + [2 for i in range(21, 41)] \
            + [3 for i in range(41, 61)] \
            + [4 for i in range(61, 81)] \
            + [5 for i in range(81, 100)]
        part = np.array(part)

        for cluster in set(part):
            axes[1].scatter(a[part == cluster, 0],
                            a[part == cluster, 1],
                            color=COLORS[cluster])
        axes[1].grid()

        # Plot #3
        hac.dendrogram(z, ax=axes[2])

        m = '\n(method: {})'.format(METHOD)
        plt.setp(
            axes[0],
            title='Screeplot{}'.format(m),
            xlabel='partition',
            ylabel='{}\ncluster distance'.format(m)
        )
        plt.setp(axes[1], title='{} clusters'.format(num_clust))
        plt.setp(axes[2], title='Dendrogram')

        fig.set_size_inches(20, 5)
        fig.savefig(str(self.driver_num) + '_cluster' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_kpi(self):
        """
        Makes a plot of KPI for every trip
        """
        print 'Plotting KPI'

        colors = \
            np.where(self.kpis['prob'] == 0, 'orange', 'gray').tolist()

        fig, axes = plt.subplots(2, 1)
        for y, axis in zip(['vR', 'a'], axes):
            self.kpis.plot(x='trip_num', y=y,
                           color=colors, kind='bar',
                           ax=axis, title=y)
            axis.legend().remove()

        fig.set_size_inches(15, 8)
        fig.savefig(str(self.driver_num) + '_kpi' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_rv(self):
        """
        Plots v(r) for every turn of each trip
        """
        print 'Plotting v(r)'

        fig, axes = plt.subplots()
        for trip, p in zip(self.trips, self.kpis['prob']):
            if p == 1:
                df = trip.trip_data
                df = df[(df.flag_turn_left == 1) | (df.flag_turn_right == 1)]
                if not df.empty:
                    df.plot(x='r', y='v', ax=axes,
                            ls='', marker='.', color='grey')
            else:
                df = trip.trip_data
                df = df[(df.flag_turn_left == 1) | (df.flag_turn_right == 1)]
                if not df.empty:
                    df.plot(x='r', y='v', ax=axes,
                            ls='', marker='.', color='orange')

        axes.legend().remove()
        axes.set_xlim([0, 50])
        axes.set_ylim([0, 15])

        fig.savefig(str(self.driver_num) + '_vR' + PLOT_EXT)
        plt.close(fig)


dr = Driver(driver_num=0)

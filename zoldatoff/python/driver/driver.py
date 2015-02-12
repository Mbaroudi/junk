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
# import random

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as dis

from sklearn.decomposition import PCA
# from itertools import cycle
from collections import Counter

# Откуда и сколько траекторий берём
DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
PLOT_EXT = '.eps'
NUM_TRIP = 10
METHOD = 'single'

# Google Chart Color List
# http://there4development.com/blog/2012/05/02/google-chart-color-list/
COLORS = [
    '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#3B3EAC',
    '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395', '#994499',
    '#22AA99', '#AAAA11', '#6633CC', '#E67300', '#8B0707', '#329262',
    '#5574A6', '#3B3EAC'] * 20


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

        # self.plot_trip()
        # self.plot_data()
        # self.plot_rv()

        # print self.kpi
        # self.trip_data.to_csv(self.driver_trip + '_trip_data.csv', sep='\t')

    # =========================================================================
    def get_data(self):
        """
        Reads trip data (x, y) from csv file
        """
        trip_filename = str(self.trip_num) + '.csv'
        trip_path = DRIVER_PATH + '/' + str(self.driver_num) + '/'
        self.trip_data = pd.DataFrame.from_csv(
            trip_path + trip_filename, index_col=False)
        self.trip_data.columns = ['x', 'y']

        self.trip_data['trip_num'] = self.trip_num
        self.trip_data['t'] = self.trip_data.index
        self.trip_data['v'] = self.distance(self.trip_data, 'x', 'y')
        self.trip_data['a'] = self.trip_data.v.diff()
        self.trip_data['r'] = self.radius(self.trip_data, 'x', 'y')
        self.trip_data['ang'] = self.angle(self.trip_data, 'x', 'y')

        self.trip_data['v'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.v, np.nan)

        self.trip_data['r'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.r, np.nan)

        self.trip_data['ang'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.ang, np.nan)

        self.trip_data['a'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.a, np.nan)

    # =========================================================================
    @staticmethod
    def turn(trip_data, turn_direction):
        df = trip_data.copy()

        if turn_direction == 'left':
            s = 1
        elif turn_direction == 'right':
            s = -1
        else:
            s = 0

        n1 = 3
        df['temp'] = df.apply(
            lambda x: 1
            if x.r < 100 and x.v > 1 and s * x.ang > 0.05
            else 0,
            axis=1)

        df['flag1'] = pd.rolling_sum(df.temp, n1) \
            .apply(lambda x: 1 if x == n1 else 0) \
            .shift(-n1/2+1)

        n2 = 6
        df['temp'] = df.apply(
            lambda x: x.ang
            if x.r < 100 and x.v > 0.1
            else - s * np.inf,
            axis=1)

        df['flag2'] = pd.rolling_sum(df.temp, n2) \
            .apply(lambda x: 1 if s * x >= np.pi / 3.0 else 0) \
            .shift(-n2/2+1)

        return np.where(df.flag1 + df.flag2 > 0, 1, 0)

    # =========================================================================
    @staticmethod
    def accel_decel(trip_data, acc_dec):
        df = trip_data.copy()

        if acc_dec == 'acc':
            s = 1
        elif acc_dec == 'dec':
            s = -1
        else:
            s = 0

        n = 3
        df['temp'] = df.a.apply(lambda x: 1 if s * x > 0.01 else 0)

        df['flag'] = pd.rolling_sum(df.temp, n) \
            .apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

        return df.flag

    # =========================================================================
    def set_flags(self):
        """
        Sets flags for special parts of trip
        """
        df = self.trip_data

        df['flag_accel'] = self.accel_decel(df, 'acc')
        df['flag_decel'] = self.accel_decel(df, 'dec')

        df['flag_turn_left'] = self.turn(df, 'left')
        df['flag_turn_right'] = self.turn(df, 'right')

        df['flag_calm'] = np.where(
            df['flag_accel'] + df['flag_decel']
            + df['flag_turn_left'] + df['flag_turn_right'] == 0, 1, 0)

        df['flag_turn'] = 0
        turn_points = set()
        dff = df[(df.flag_turn_right == 1) | (df.flag_turn_left == 1)]
        for k, row in dff.iterrows():
            i = k
            while True:
                i += 1
                if df.ix[i].flag_turn == 0 and (
                        df.ix[i].flag_accel == 1
                        or df.ix[i].flag_turn_left == 1
                        or df.ix[i].flag_turn_right == 1):
                    turn_points.add(i)
                else:
                    break

            i = k
            while True:
                i -= 1
                if df.ix[i].flag_turn == 0 and (
                        df.ix[i].flag_decel == 1
                        or df.ix[i].flag_turn_left == 1
                        or df.ix[i].flag_turn_right == 1):
                    turn_points.add(i)
                else:
                    break

        df.ix[df['t'].isin(turn_points), 'flag_turn'] = 1

    # =========================================================================
    def get_kpi(self):
        df = self.trip_data
        kpi = pd.Series(None)

        kpi['driver_trip'] = self.driver_trip
        kpi['driver_num'] = self.driver_num
        kpi['trip_num'] = self.trip_num

        # vR = наибольшая скорость вхождения в поворот с радиусом 15 м.
        df_turn = df[(df.flag_turn_left == 1) | (df.flag_turn_right == 1)]
        # kpi['vR'] = df_turn[df_turn.r <= 10].v.max()
        kpi['vR'] = self.decile(df_turn[df_turn.r <= 15], 'v')

        kpi['a'] = self.decile(df[df.flag_accel == 1], 'a')

        # accel = наибольшее ускорение после прохождения поворота
        # decel = наибольшее замедление перед прохождением поворота
        # kpi['accel'] = df[(df.flag_accel == 1) & (df.flag_turn == 1)].a.max()
        # kpi['decel'] = df[(df.flag_decel == 1) & (df.flag_turn == 1)].a.max()
        kpi['accel'] = self.decile(
            df[(df.flag_accel == 1) & (df.flag_turn == 1)], 'a')
        kpi['decel'] = self.decile(
            df[(df.flag_decel == 1) & (df.flag_turn == 1)], 'a')

        # calm = доля участков пути, на которых нет ускорений и поворотов
        # в общей длине пути (только там, где скорость больше 5 м/с)
        n1 = len(df[(df.flag_calm == 1) & (df.v > 5.0)])
        n2 = len(df[df.v > 5.0])
        if n2 > 0:
            kpi['calm'] = float(n1) / float(n2)
        else:
            kpi['calm'] = 0.5

        # nerv_a = количество кратковременных нажатий на педаль газа
        # nerv_ang = количество небольших поворотов руля
        kpi['nerv_a'] = abs(df.flag_calm.diff()).sum() / \
            float(len(df[df.flag_calm == 1]))
        kpi['nerv_ang'] = abs(df[df['flag_turn'] == 0].ang).sum() / \
            float(len(df[df.flag_turn == 0]))

        kpi['s'] = df.v.sum()

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

        fig.set_size_inches(15, 10)
        fig.savefig(self.driver_trip + '_data' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_trip(self):
        """
        Сторит 2 графика:
        * график поворотов / разгонов / торможений
        * график поворотов с примыкающими к ним разгонами и торможениями
        """
        df = self.trip_data

        # График, на котором выделены повороты и
        # участки разгона / торможения

        fig, axes = plt.subplots()

        df.plot(x='x', y='y', ax=axes, color='gray')

        if not df[df.flag_accel == 1].empty:
            df[df.flag_accel == 1].plot(x='x', y='y', ax=axes, color='orange',
                                        ls='', marker='.')

        if not df[df.flag_decel == 1].empty:
            df[df.flag_decel == 1].plot(x='x', y='y', ax=axes, color='green',
                                        ls='', marker='.')

        if not df[df.flag_turn_left == 1].empty:
            df[df.flag_turn_left == 1].plot(x='x', y='y', ax=axes, color='r',
                                            ls='', marker='o')

        if not df[df.flag_turn_right == 1].empty:
            df[df.flag_turn_right == 1].plot(x='x', y='y', ax=axes, color='b',
                                             ls='', marker='o')

        df[df.index <= 10].plot(x='x', y='y', ax=axes, color='r',
                                         ls='', marker='x')

        axes.legend(['trip', 'accel', 'decel', 'left', 'right', 'start'])

        axes.autoscale()
        plt.axis('equal')

        fig.savefig(self.driver_trip + '_trip' + PLOT_EXT)
        plt.close(fig)

        # График, на котором выделены повороты =
        # замедление до поворота + поворот + ускорение после поворота

        fig, axes = plt.subplots()

        df.plot(x='x', y='y', ax=axes, color='gray')

        if not df[df.flag_turn == 1].empty:
            df[df.flag_turn == 1].plot(x='x', y='y', ax=axes, color='red',
                                       ls='', marker='.')

        axes.autoscale()
        plt.axis('equal')
        axes.legend(['trip', 'turn'])

        fig.savefig(self.driver_trip + '_turn' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_rv(self):
        """
        Строит график зависимости скорости от радиуса поворота
        Для графика выбираются только точки, размеченные как повороты
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

    # =========================================================================
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

        ang = np.where(ang > np.pi, ang - 2.0*np.pi, ang)
        ang = np.where(ang < -np.pi, ang + 2.0*np.pi, ang)

        return ang

    @staticmethod
    def decile(df, x):
        """
        Returns minimum value in upper decile
        """
        d = df[x].sort(x, inplace=False).tolist()
        l = len(d)
        if l == 0:
            return 0
        else:
            return d[int(0.9*l)]


# =============================================================================
# =============================================================================
class Driver(object):
    """
    Driver is a class that contains:
     * trips data
     * method for clustering KPI's
     * methods for data visualization
    """
    def __init__(self, driver_num=1, method='csv'):
        """
        Loads trip (or KPI) data from files
        """
        self.driver_num = driver_num

        if method == 'csv':
            self.get_data()
            self.cluster()
            # self.pca()
            self.save_kpi()
            # self.plot_rv()

        else:
            self.load_kpi()
            # self.pca()

        # self.plot_kpi()
        # self.plot_trips()
        # print self.kpis

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
        self.kpis.to_csv(str(self.driver_num) + '.txt', index=False, sep='\t')

    # =========================================================================
    def load_kpi(self):
        """
        Loads KPI data from disk
        """
        file_fullname = str(self.driver_num) + '.txt'
        self.kpis = pd.DataFrame.from_csv(file_fullname,
                                          index_col=False, sep='\t')

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

        # columns = ['vR', 's', 'a', 'accel', 'calm', 'nerv_a', 'nerv_ang']  # 'decel'
        columns = ['vR', 's']
        kpis = self.kpis[columns].copy()
        for column in columns:
            self.normalize(kpis, column)
            kpis[column].fillna(0.5, inplace=True)

        matr = kpis.as_matrix(columns=columns)
        a = dis.squareform(dis.pdist(matr))
        z = hac.linkage(a, method=METHOD)
        knee = np.diff(z[::-1, 2], 2)
        # knee[knee.argmax()] = 0
        num_clust = knee.argmax() + 2
        part = hac.fcluster(z, num_clust, 'maxclust')

        # The biggest cluster
        mc = Counter(part).most_common(1)[0][0]
        self.kpis['prob'] = [1 if p == mc else 0 for p in part.tolist()]

        self.plot_cluster(a, z, knee, num_clust, part)

    # =========================================================================
    def pca(self):
        """
        Principal component analysis
        # http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
        """

        columns = ['vR', 's', 'a', 'accel', 'decel', 'calm', 'nerv_a', 'nerv_ang']
        kpis = self.kpis[columns].copy()
        for column in columns:
            self.normalize(kpis, column)
            kpis[column].fillna(0.5, inplace=True)

        print kpis.columns
        X = kpis.as_matrix(columns=columns)
        pca = PCA()
        pca.fit(X)
        print(pca.explained_variance_ratio_)

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
        if self.driver_num == 0:
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

        fig, axes = plt.subplots(8, 1)
        for y, axis in zip(
                ['vR', 's', 'a', 'accel', 'decel', 'calm', 'nerv_a', 'nerv_ang'],
                axes):
            self.kpis.plot(x='trip_num', y=y,
                           color=colors, kind='bar',
                           ax=axis, title=y)
            axis.legend().remove()

        fig.set_size_inches(15, 10)
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

    # =========================================================================
    def plot_trips(self):
        """
        Plots all trips of a driver
        """
        print 'Plotting trips'

        if self.driver_num == 0:
            color_num  = [1 for i in range(1, 21)] \
                + [2 for i in range(21, 41)] \
                + [3 for i in range(41, 61)] \
                + [4 for i in range(61, 81)] \
                + [5 for i in range(81, 101)]

        fig, axes = plt.subplots()
        for trip, p in zip(self.trips, self.kpis['prob']):
            if self.driver_num == 0:
                trip.trip_data.plot(x='x', y='y', ax=axes, ls='--',
                                    color=COLORS[color_num[trip.trip_num-1]])

            elif p == 1:
                trip.trip_data.plot(x='x', y='y', ax=axes,
                                    color=COLORS[trip.trip_num], ls=':')
            else:
                trip.trip_data.plot(x='x', y='y', ax=axes, color='r')

        axes.autoscale()
        plt.axis('equal')
        axes.legend().remove()
        fig.savefig(str(self.driver_num) + '_trips' + PLOT_EXT)
        plt.close(fig)


# =============================================================================
# =============================================================================
# =============================================================================
def save_result():
    """
    Saves the result to a file for submission
    """
    print 'Saving results'

    result_file_name = 'submission.csv'
    result_df = pd.DataFrame(None, columns=['driver_trip', 'prob'])

    for file_name in os.listdir('./'):
        file_ext = os.path.splitext(file_name)[1]
        if file_ext == '.txt':
            df = pd.DataFrame.from_csv(file_name, index_col=False, sep='\t')
            df.prob = df.prob.map(int).map(str)
            result_df = result_df.append(df[['driver_trip', 'prob']])

    result_df.to_csv(result_file_name, sep=',', index=False)

# =============================================================================
# =============================================================================
# =============================================================================

# dr = Driver(driver_num=0, method='csv')

dirs = os.listdir(DRIVER_PATH)
dirs = [x for x in dirs if not x.startswith('.')]
dirs = map(int, dirs)
dirs.sort()
for i in dirs:
    Driver(driver_num=i)

save_result()

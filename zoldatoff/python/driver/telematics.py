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
import seaborn as sns

import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as dis

from collections import Counter
from pykalman import KalmanFilter


# Откуда и сколько траекторий берём
DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
DRIVER_NUM = 0
NUM_CSV = 30
DEBUG = 1
EXT = '.png'

DS_MIN = 1.0          # Минимальное расстояние для расчёта радиус поворота
VELOCITY_LOW = 5.0    # Участок ускорения отбирается для скоростей из диапазона
VELOCITY_HIGH = 15.0  # между VELOCITY_LOW и VELOCITY_HIGH
ACCEL_MINLEN = 10.0   # Длина участка разгона не менее ACCEL_MINLEN точек
ACCEL_TAIL = 3        # В конце разгона ускорение снижается - отбрасываем

DISTANCE_MAX = 40.0
ACCELERATION_MAX = 12.0

ANALYTICS_RADIUS = 30  # Измеряем максимальную скорость вхождения в этот радиус

METHOD = 'single'

# COLORS = [
#     '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
#     '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
#     ##
#     '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
#     '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC'
# ]

COLORS = [
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E',
    #
    '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
    '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
    #
    '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
    '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC',
    #
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E',
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E',
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E',
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E',
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E',
    '#FA4E9B', '#43AE18', '#1095BE', '#8C4104', '#6D42B0', '#084531',
    '#DDB505', '#F3250D', '#B1B46F', '#691930', '#F15FFF', '#EF847F',
    '#442757', '#276802', '#E693B8', '#25918D', '#B32323', '#0A3852',
    '#F48FFB', '#DE26AA', '#4DA7EF', '#337236', '#86BB38', '#BC206E']


class Trip(object):
    """
    This class:
     * reads trip data from csv file
     * smooths data using Kalman filter
     * calculates velocity, acceleration and turn radius for every point
     * calculates KPI's for the trip

    KPI's include:
     * maximum velocity
     * maximum acceleration
     * maximum velocity in turn with radius < ANALYTICS_RADIUS
     * maximum acceleration on the accelerating parts of the trip

    """
    # @profile
    def __init__(self, driver_num=1, trip_num=1):
        print 'Driver =', str(driver_num), ', trip =', str(trip_num)

        self.driver_num = driver_num
        self.trip_num = trip_num

        self.df_from_csv()
        self.df_kalman()
        self.df_physics()
        # self.df_kalman_ang()
        self.df_acceleration()
        self.df_kpi()

        if DEBUG >= 1:
            self.plot_velocity()
            self.plot_trip()

        if DEBUG >= 2:
            print self.trip_df[['t', 'x_', 'y_', 'x', 'y', 'v', 'a', 'r']]
            print self.kpi

# =============================================================================
    def df_from_csv(self):
        """
        Reads trip data (x, y) from csv file
        """
        trip_file_name = str(self.trip_num) + '.csv'
        trip_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
        self.trip_df = pd.DataFrame.from_csv(
            trip_file_path + trip_file_name,
            index_col=False
        )
        self.trip_df.columns = ['x_', 'y_']

# =============================================================================
    @staticmethod
    def distance(df, x, y):
        return np.sqrt(
            np.square(df[x] - df[x].shift(1))
            +
            np.square(df[y] - df[y].shift(1))
        )

# =============================================================================
    def df_kalman(self):
        """
        Smooths trip using Kalman method
         * https://github.com/pykalman/pykalman
         * http://pykalman.github.io
         * https://ru.wikipedia.org/wiki/Фильтр_Калмана
         * http://bit.ly/1Dd1bhn
        """
        df = self.trip_df.copy()

        df['ds'] = self.distance(df, 'x_', 'y_')

        # Маскируем ошибочные точки
        df['x_'] = np.where(df['ds'] > DISTANCE_MAX, np.ma.masked, df['x_'])
        df['y_'] = np.where(df['ds'] > DISTANCE_MAX, np.ma.masked, df['y_'])

        df['vx'] = df['x_'] - df['x_'].shift(1)
        df['vy'] = df['y_'] - df['y_'].shift(1)

        transition_matrix = [[1, 0, 1, 0],
                             [0, 1, 0, 1],
                             [0, 0, 1, 0],
                             [0, 0, 0, 1]]
        observation_matrix = [[1, 0, 0, 0],
                              [0, 1, 0, 0]]
        xinit, yinit = df['x_'][0], df['y_'][0]
        vxinit, vyinit = df['vx'][1], df['vy'][1]
        initcovariance = 1.0e-4 * np.eye(4)
        transistionCov = 1.0e-3 * np.eye(4)
        observationCov = 1.0e-2 * np.eye(2)

        # Фильтр Калмана
        kfilter = KalmanFilter(
            transition_matrices=transition_matrix,
            observation_matrices=observation_matrix,
            initial_state_mean=[xinit, yinit, vxinit, vyinit],
            initial_state_covariance=initcovariance,
            transition_covariance=transistionCov,
            observation_covariance=observationCov
        )
        measurements = df[['x_', 'y_']].values
        kfilter = kfilter.em(measurements, n_iter=5)
        (state_means, state_covariances) = kfilter.smooth(measurements)

        kdf = pd.DataFrame(state_means, columns=('x', 'y', 'vx', 'vy'))
        kdf['v'] = np.sqrt(np.square(kdf['vx']) + np.square(kdf['vy']))

        self.trip_df[['x', 'y', 'v']] = kdf[['x', 'y', 'v']]

# =============================================================================
    @staticmethod
    def normalize_angle(a):
        if a > np.pi:
            return a - 2.0*np.pi
        elif a < -np.pi:
            return a + 2.0*np.pi
        else:
            return a

# =============================================================================
    def df_physics(self):
        """
        Calculates:
         * distance
         * velocity
         * acceleration
         * angle
         * angular speed
         * turn radius
        """
        df = self.trip_df.copy()

        # время
        df['t'] = df.index

        # дельта времени
        # df['dt'] = df['t'] - df['t'].shift(1)

        # расстояние
        df['ds'] = self.distance(df, 'x', 'y')

        # ускорение
        df['a'] = (df['v'] - df['v'].shift(1))  # / df['dt']

        # направление движения
        df['ang'] = np.where(
            (df['ds'] > DS_MIN) & (df['ds'] < DISTANCE_MAX),
            np.arctan2(
                df['y'] - df['y'].shift(1),
                df['x'] - df['x'].shift(1)
            ),
            np.nan
        )

        # Исправляем ошибочные данные
        df['x'] = np.where(df['ds'] > DISTANCE_MAX, np.nan, df['x'])
        df['y'] = np.where(df['ds'] > DISTANCE_MAX, np.nan, df['y'])
        df['ds'] = np.where(df['ds'] > DISTANCE_MAX, np.nan, df['ds'])
        df['a'] = np.where(df['a'] > ACCELERATION_MAX, np.nan, df['a'])

        # смена направления движения
        df['dang'] = df['ang'] - df['ang'].shift(1)
        df['dang'] = df['dang'].apply(self.normalize_angle)

        # радиус поворота
        df['r'] = np.where(
            np.all(df['dang'].shift(i) > 0.1 for i in range(-2, 3)),
            sum([df['ds'].shift(i) for i in range(-2, 3)])
            / abs((df['ang'].shift(2) - df['ang'].shift(-2)
                   ).apply(self.normalize_angle) + 0.00001
                  ),
            np.nan
        )

        self.trip_df[['t', 'a', 'r']] = df[['t', 'a', 'r']]

# =============================================================================
    def df_acceleration(self):
        """
        Function searches for acceleration parts of trajectory
        """

        df = self.trip_df.copy()
        df['accel'] = 0
        accel = set()
        n = 0

        row_iterator = df.iterrows()
        prev = row_iterator.next()

        for i, curr in row_iterator:
            if len(accel) == 0 and VELOCITY_LOW < curr['v'] < VELOCITY_HIGH:
                accel.add(curr['t'])

            elif len(accel) > 0 \
                    and VELOCITY_LOW < curr['v'] \
                    and (curr['a'] > 0.0 or prev['a'] > 0.0):
                accel.add(curr['t'])

            elif len(accel) > ACCEL_MINLEN \
                    and curr['a'] < 0.0 \
                    and prev['a'] < 0.0:
                n += 1
                df.ix[df['t'].isin(accel), 'accel'] = n
                accel.clear()

            else:
                accel.clear()

            prev = curr

        self.trip_df['accel'] = df['accel']

# =============================================================================
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
    def df_kpi(self):
        """
        Defines KPI's for the driver:
         * maximum velocity
         * maximum acceleration
         * maximum velocity in turn with radius < ANALYTICS_RADIUS
         * maximum acceleration on the accelerating parts of the trip
        """
        kpi = {'driver_num': self.driver_num,
               'trip_num': self.trip_num,
               'bad': False
               }

        # df = self.trip_df[self.trip_df['v'] > 0.0]
        # kpi['v'] = self.decile(df, 'v')

        # df = self.trip_df[(self.trip_df['a'] > 0.0)
        #                    &
        #                    (self.trip_df['v'] > 5.0)]
        # kpi['a'] = self.decile(df, 'a')

        df = self.trip_df[self.trip_df['r'] <= ANALYTICS_RADIUS]
        kpi['v_r'] = self.decile(df, 'v')

        df = self.trip_df[self.trip_df['accel'] > 0]
        kpi['accel'] = self.decile(df, 'a')

        if abs(self.trip_df['x_'] - self.trip_df['x']).mean() > 1.0:
            kpi['bad'] = True
        elif abs(self.trip_df['y_'] - self.trip_df['y']).mean() > 1.0:
            kpi['bad'] = True
        elif self.trip_df['x'].max() - self.trip_df['x'].min() < 50.0:
            kpi['bad'] = True
        elif self.trip_df['y'].max() - self.trip_df['y'].min() < 50.0:
            kpi['bad'] = True
        elif kpi['v_r'] > DISTANCE_MAX:
            # or kpi['v'] > DISTANCE_MAX
            kpi['bad'] = True
        elif kpi['accel'] > ACCELERATION_MAX:
            # or kpi['a'] > ACCELERATION_MAX
            kpi['bad'] = True
        elif kpi['v_r'] < 1.0:
            # or kpi['v'] < 1.0
            kpi['bad'] = True
        elif kpi['accel'] < 0.1:
            # or kpi['a'] < 0.1
            kpi['bad'] = True

        if kpi['bad']:
            kpi['v_r'] = kpi['accel'] = np.nan
            # = kpi['v'] = kpi['a'] =

        self.kpi = kpi  # pd.DataFrame.from_dict(kpi)

# =============================================================================
    def plot_velocity(self):
        """
        Makes a plot v(t) for one particuls trip and shows acceleration parts
        """
        fig, axes = plt.subplots()

        kpi_v = self.kpi['v_r']

        df = self.trip_df[self.trip_df['v'] < kpi_v]
        if not df.empty:
            df.plot(x='t', y='v', ax=axes, ls='', marker='.', color='k')

        df = self.trip_df[self.trip_df['v'] >= kpi_v]
        if not df.empty:
            df.plot(x='t', y='v', ax=axes, ls='', marker='.', color='r')

        axes.autoscale()
        # axes.legend().remove()
        # axes.set_xlim([0, 100])
        sns.despine()
        fig.savefig(
            str(self.driver_num) + '_' + str(self.trip_num) + '_v(t)' + EXT
        )
        plt.close(fig)

# =============================================================================
    def plot_trip(self):
        """
        Makes a plot v(t) for one particuls trip and shows acceleration parts
        """

        df = self.trip_df
        fig, axes = plt.subplots()

        df[df.index < 100].plot(
            x='x_', y='y_', ax=axes,
            ls='-', marker='.', color='k', title='original')

        df[df.index < 100].plot(
            x='x', y='y', ax=axes,
            ls='-', marker='.', color='r', title='Kalman')

        axes.autoscale()
        axes.legend().remove()
        sns.despine()
        fig.savefig(str(self.driver_num) + '_' + str(self.trip_num)
                    + '_smooth' + EXT)
        plt.close(fig)


# =============================================================================
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
            self.trips = []
            self.kpis = pd.DataFrame(None, columns=[
                'driver_num', 'trip_num', 'v_r', 'accel'])  # 'v', 'a',

            trip_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
            files = os.listdir(trip_file_path)

            for file_name in random.sample(files, NUM_CSV):
                # ['121.csv', '124.csv', '151.csv', '159.csv']
                # ['55.csv', '108.csv', '115.csv', '106.csv']:
                # ['10.csv', '100.csv', '105.csv', '110.csv', '114.csv']:
                # ['15.csv', '83.csv', '84.csv', '88.csv', '102.csv']
                # random.sample(files, NUM_CSV):
                trip_num = int(os.path.splitext(file_name)[0])
                trip = Trip(driver_num, trip_num)
                self.trips.append(trip)
                self.kpis = self.kpis.append(trip.kpi, ignore_index=True)

            self.kpis.sort(['driver_num', 'trip_num'], inplace=True)
            self.cluster()
            self.save_kpi()

        else:
            self.load_kpi()

        if len(self.kpis) >= 4:
            if method == 'csv':
                self.plot_trips()
                self.plot_turns()
                self.plot_v()

            self.plot_kpi()
            self.plot_hist()

# =============================================================================
    def save_kpi(self):
        """
        Saves KPI data to disk
        """
        self.kpis.to_csv(str(self.driver_num) + '.txt', index=False)

# =============================================================================
    def load_kpi(self):
        """
        Loads KPI data from disk
        """
        file_fullname = str(self.driver_num) + '.txt'
        self.kpis = pd.DataFrame.from_csv(file_fullname, index_col=False)

# =============================================================================
    @staticmethod
    def normalize(df, column):
        df_min, df_max = df[column].min(), df[column].max()
        if df_min == df_max:
            df[column] = 0.5,
        else:
            df[column] -= df_min
            df[column] /= df_max - df_min

        return df

# =============================================================================
    def cluster(self):
        """
        Scales and clusters KPI data
        http://stackoverflow.com/questions/21638130/tutorial-for-scipy-cluster-hierarchy
        """

        columns = ['v_r', 'accel']  # 'v', 'a',
        kpis = self.kpis[columns].copy()
        for column in columns:
            self.normalize(kpis, column)
            kpis[column].fillna(0.5, inplace=True)

        matr = kpis.as_matrix(columns=columns)
        a = dis.squareform(dis.pdist(matr))
        z = hac.linkage(a, method=METHOD)
        knee = np.diff(z[::-1, 2], 2)
        # num_clust = knee.argmax() + 2
        knee[knee.argmax()] = 0
        num_clust = knee.argmax() + 2
        part = hac.fcluster(z, num_clust, 'maxclust')

        mc = Counter(part).most_common(1)[0][0]
        self.kpis['prob'] = [1 if p == mc else 0 for p in part.tolist()]

        self.plot_cluster(a, z, knee, num_clust, part)

# =============================================================================
    def plot_cluster(self, a, z, knee, num_clust, part):
        """
        Makes a plot of clustering result
        """
        print 'Plotting cluster'

        fig, axes = plt.subplots(1, 3)
        sns.set_style("whitegrid")

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

        # plt.tight_layout()
        fig.set_size_inches(20, 5)
        sns.despine()
        fig.savefig(str(self.driver_num) + '_cluster' + EXT)
        plt.close(fig)

# =============================================================================

    def plot_v(self):
        """
        Makes a plot v(t)
        """

        print 'Plotting v(t)'

        fig, axes = plt.subplots()

        n_0 = n_1 = 0
        for trip, p in zip(self.trips, self.kpis['prob']):
            if p == 1 and n_1 < 5:
                n_1 += 1
                trip.trip_df.plot(x='t', y='v', ax=axes, color='k', ls=':')
            elif p == 0 and n_0 < 5:
                n_0 += 1
                trip.trip_df.plot(x='t', y='v', ax=axes, color='r', ls=':')

        axes.set_xlim([0, 600])
        axes.set_ylim([0, 40])
        axes.legend().remove()
        sns.despine()
        fig.savefig(str(self.driver_num) + '_v(t)' + EXT)
        plt.close(fig)


# =============================================================================
    def plot_kpi(self):
        """
        Makes a plot of KPI for every trip
        """
        print 'Plotting KPI'

        colors = \
            np.where(self.kpis['prob'] == 0, 'red', 'gray').tolist()

        fig, axes = plt.subplots(2, 1)
        for y, axis in zip(['v_r', 'accel'], axes):  # 'v', 'a',
            self.kpis.plot(x='trip_num', y=y,
                           color=colors, kind='bar',
                           ax=axis, title=y)
            axis.legend().remove()

        fig.set_size_inches(20, 10)
        sns.despine()
        fig.savefig(str(self.driver_num) + '_kpi' + EXT)
        plt.close(fig)

# =============================================================================
    def plot_trips(self):
        """
        Plots all trips of a driver
        """
        print 'Plotting trips'

        fig, axes = plt.subplots()
        for trip, p in zip(self.trips, self.kpis['prob']):
            if p == 1:
                trip.trip_df.plot(x='x', y='y', ax=axes, color='k', ls=':')
            else:
                trip.trip_df.plot(x='x', y='y', ax=axes, color='r')

        axes.autoscale()
        axes.legend().remove()
        sns.despine()
        fig.savefig(str(self.driver_num) + '_trips' + EXT)
        plt.close(fig)

# =============================================================================
    def plot_turns(self):
        """
        Plots v(r) for every turn of each trip
        """
        print 'Plotting v(r)'

        fig, axes = plt.subplots()
        for trip, p in zip(self.trips, self.kpis['prob']):
            if p == 1:
                trip.trip_df.plot(x='r', y='v', ax=axes,
                                    ls='', marker='.', color='grey')
            else:
                trip.trip_df.plot(x='r', y='v', ax=axes,
                                    ls='', marker='.', color='red')

        axes.legend().remove()
        axes.set_xlim([0, 50])
        axes.set_ylim([0, 15])
        sns.despine()
        fig.savefig(str(self.driver_num) + '_turns' + EXT)
        plt.close(fig)

# =============================================================================
    def plot_hist(self):
        """
        Plots histograms of KPI's for all trips
        """
        print 'Plotting histograms'

        fig, axes = plt.subplots()
        self.kpis[['v_r', 'accel']].hist(ax=axes, bins=50)  # 'v', 'a',
        sns.despine()
        fig.savefig(str(self.driver_num) + '_hist' + EXT)
        plt.close(fig)


# =============================================================================
# =============================================================================
# =============================================================================
def save_result():
    """
    Saves the result to a file for submission
    """
    result_file_name = 'submission.csv'
    result_df = pd.DataFrame(None, columns=['driver_trip', 'prob'])

    for file_name in os.listdir('./'):
        file_ext = os.path.splitext(file_name)[1]
        if file_ext == '.txt':
            df = pd.DataFrame.from_csv(file_name)
            df['driver_trip'] = \
                df.driver_num.map(int).map(str) \
                + '_' \
                + df.trip_num.map(int).map(str)
            df.prob = df.prob.map(int).map(str)
            result_df = result_df.append(df[['driver_trip', 'prob']])

    result_df.to_csv(result_file_name, sep=',', index=False)

# =============================================================================
# =============================================================================
# =============================================================================


# dr = Driver(DRIVER_NUM, method='load')
dr = Driver(DRIVER_NUM, method='csv')
# for n in [1,2,3,10,11,12]:
#     dr = Driver(n, method='csv')

# print 'Bad'
# print dr.kpis[dr.kpis['bad'] == True]['trip_num']

# print 'Result'
# print dr.kpis[dr.kpis['prob'] == 0][['trip_num', 'v', 'v_r']]

# print 'Save result to file'
# save_result()

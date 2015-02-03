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
DRIVER_NUM = 1
NUM_CSV = 20
DEBUG = 2
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


class Track(object):
    """
    This class:
     * reads track data from csv file
     * smooths data using Kalman filter
     * calculates velocity, acceleration and turn radius for every point
     * calculates KPI's for the track

    KPI's include:
     * maximum velocity
     * maximum acceleration
     * maximum velocity in turn with radius < ANALYTICS_RADIUS
     * maximum acceleration on the accelerating parts of the track

    """
    # @profile
    def __init__(self, driver_num=1, track_num=1):
        print 'Driver =', str(driver_num), ', track =', str(track_num)

        self.driver_num = driver_num
        self.track_num = track_num

        self.cvs_to_df()
        self.df_kalman()
        self.df_physics()
        self.acceleration()

        self.key_indicator()

        if DEBUG >= 1:
            self.plot_velocity()
            self.plot_ang()

        if DEBUG >= 2:
            print self.track_df[['t', 'x_', 'y_', 'vx_', 'vy_',
                                 'x', 'y', 'v', 'a']]
            print self.kpi

# =============================================================================
    def cvs_to_df(self):
        """
        Reads track data (x, y) from csv file
        """
        track_file_name = str(self.track_num) + '.csv'
        track_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
        self.track_df = pd.DataFrame.from_csv(
            track_file_path + track_file_name,
            index_col=False
        )
        self.track_df.columns = ['x_', 'y_']

# =============================================================================
    def df_kalman(self, method='smooth'):
        """
        Smooths track using Kalman method
         * https://github.com/pykalman/pykalman
         * http://pykalman.github.io
         * https://ru.wikipedia.org/wiki/Фильтр_Калмана
         * http://bit.ly/1Dd1bhn
        """
        df = self.track_df

        # Plot beginning
        if DEBUG >= 1:
            fig, axes = plt.subplots()
            df[df.index < 100].plot(
                x='x_', y='y_', ax=axes, ls='-', marker='.',
                color='k', title='original')

        df['ds_'] = np.sqrt(
            np.square(df['x_'] - df['x_'].shift(1))
            +
            np.square(df['y_'] - df['y_'].shift(1))
        )

        # Маскируем ошибочные точки
        df['x_'] = np.where(df['ds_'] > DISTANCE_MAX, np.ma.masked, df['x_'])
        df['y_'] = np.where(df['ds_'] > DISTANCE_MAX, np.ma.masked, df['y_'])

        df['vx_'] = df['x_'] - df['x_'].shift(1)
        df['vy_'] = df['y_'] - df['y_'].shift(1)

        transition_matrix = [[1, 0, 1, 0],
                             [0, 1, 0, 1],
                             [0, 0, 1, 0],
                             [0, 0, 0, 1]]
        observation_matrix = [[1, 0, 0, 0],
                              [0, 1, 0, 0]]
        vxinit = df['vx_'][1]
        vyinit = df['vy_'][1]
        initcovariance = 1.0e-4 * np.eye(4)
        transistionCov = 1.0e-3 * np.eye(4)
        observationCov = 1.0e-2 * np.eye(2)

        # Фильтр Калмана
        kfilter = KalmanFilter(
            transition_matrices=transition_matrix,
            observation_matrices=observation_matrix,
            initial_state_mean=[0, 0, vxinit, vyinit],
            initial_state_covariance=initcovariance,
            transition_covariance=transistionCov,
            observation_covariance=observationCov
        )
        measurements = df[['x_', 'y_']].values
        kfilter = kfilter.em(measurements, n_iter=5)

        if method == 'filter':
            (state_means, state_covariances) = kfilter.filter(measurements)
        elif method == 'smooth':
            (state_means, state_covariances) = kfilter.smooth(measurements)

        kalman_df = pd.DataFrame(state_means, columns=('x', 'y', 'vx', 'vy'))

        # Plot continue
        if DEBUG >= 1:
            kalman_df[kalman_df.index < 100].plot(
                x='x', y='y', ax=axes, ls='-', marker='.',
                color='r', title='Kalman')
            axes.autoscale()
            axes.legend().remove()
            sns.despine()
            fig.savefig(str(self.driver_num) + '_' + str(self.track_num)
                        + '_' + method + EXT)
            plt.close(fig)

        self.track_df['x'] = kalman_df['x']
        self.track_df['y'] = kalman_df['y']
        self.track_df['vx'] = kalman_df['vx']
        self.track_df['vy'] = kalman_df['vy']

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
        df = self.track_df

        # время
        df['t'] = df.index

        # дельта времени
        df['dt'] = df['t'] - df['t'].shift(1)

        # расстояние
        df['ds'] = np.sqrt(
            np.square(df['x'] - df['x'].shift(1))
            +
            np.square(df['y'] - df['y'].shift(1))
        )

        # скорость
        # df['v'] = df['ds'] / df['dt']
        df['v'] = np.sqrt(np.square(df['vx']) + np.square(df['vy']))

        # ускорение
        df['a'] = (df['v'] - df['v'].shift(1)) / df['dt']

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
        df['dang'] = df['dang'].apply(
            lambda x: x - 2.0*np.pi if x > np.pi else x
        )
        df['dang'] = df['dang'].apply(
            lambda x: x + 2.0*np.pi if x < -np.pi else x
        )

        # радиус поворота
        df['r'] = \
            (df['ds'] + df['ds'].shift(1)) / 2.0 / (abs(df['dang']) + 0.000001)

        self.track_df = df

# =============================================================================
    def acceleration(self):
        """
        Function searches for acceleration parts of trajectory
        """

        self.track_df['accel'] = 0
        accel = set()
        n = 0

        row_iterator = self.track_df.iterrows()
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
                self.track_df.ix[self.track_df['t'].isin(accel), 'accel'] = n
                accel.clear()

            else:
                accel.clear()

            prev = curr

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
    def key_indicator(self):
        """
        Defines KPI's for the driver:
         * maximum velocity
         * maximum acceleration
         * maximum velocity in turn with radius < ANALYTICS_RADIUS
         * maximum acceleration on the accelerating parts of the track
        """
        kpi = {'driver_num': self.driver_num,
               'track_num': self.track_num,
               'bad': False
               }

        df = self.track_df[self.track_df['v'] > 0.0]
        kpi['v'] = self.decile(df, 'v')

        df = self.track_df[(self.track_df['a'] > 0.0)
                           &
                           (self.track_df['v'] > 5.0)]
        kpi['a'] = self.decile(df, 'a')

        df = self.track_df[self.track_df['r'] <= ANALYTICS_RADIUS]
        kpi['v_r'] = self.decile(df, 'v')

        df = self.track_df[self.track_df['accel'] > 0]
        kpi['accel'] = self.decile(df, 'a')

        if abs(self.track_df['x_'] - self.track_df['x']).mean() > 1.0:
            kpi['bad'] = True
        elif abs(self.track_df['y_'] - self.track_df['y']).mean() > 1.0:
            kpi['bad'] = True
        elif self.track_df['x'].max() - self.track_df['x'].min() < 50.0:
            kpi['bad'] = True
        elif self.track_df['y'].max() - self.track_df['y'].min() < 50.0:
            kpi['bad'] = True
        elif kpi['v'] > DISTANCE_MAX or kpi['v_r'] > DISTANCE_MAX:
            kpi['bad'] = True
        elif kpi['a'] > ACCELERATION_MAX or kpi['accel'] > ACCELERATION_MAX:
            kpi['bad'] = True
        elif (kpi['v'] < 1.0 or kpi['v_r'] < 1.0
              or kpi['a'] < 0.1 or kpi['accel'] < 0.1):
            kpi['bad'] = True

        if kpi['bad']:
            kpi['a'] = kpi['v_r'] = kpi['accel'] = kpi['v'] = np.nan

        self.kpi = kpi

# =============================================================================
    def plot_velocity(self):
        """
        Makes a plot v(t) for one particuls track and shows acceleration parts
        """
        fig, axes = plt.subplots()

        kpi_v = self.kpi['v']

        df = self.track_df[self.track_df['v'] < kpi_v]
        if not df.empty:
            df.plot(x='t', y='v', ax=axes, ls='', marker='.', color='k')

        df = self.track_df[self.track_df['v'] >= kpi_v]
        if not df.empty:
            df.plot(x='t', y='v', ax=axes, ls='', marker='.', color='r')

        axes.autoscale()
        #axes.legend().remove()
        # axes.set_xlim([0, 100])
        sns.despine()
        fig.savefig(
            str(self.driver_num) + '_' + str(self.track_num) + '_v(t)' + EXT
        )
        plt.close(fig)

# =============================================================================
    def plot_ang(self):
        """
        Makes a plot v(t) for one particuls track and shows acceleration parts
        """
        fig, axes = plt.subplots()


        self.track_df.plot(x='t', y='dang', ax=axes)

        # axes.autoscale()
        # axes.legend().remove()
        # axes.set_xlim([0, 100])
        sns.despine()
        fig.savefig(
            str(self.driver_num) + '_' + str(self.track_num) + '_ang(t)' + EXT
        )
        plt.close(fig)

# =============================================================================
# =============================================================================
# =============================================================================
class Driver(object):
    """
    Driver is a class that contains:
     * tracks data
     * method for clustering KPI's
     * methods for data visualization
    """
    # @profile
    def __init__(self, driver_num=1, method='csv'):
        """
        Loads track (or KPI) data from files
        """
        self.driver_num = driver_num

        if method == 'csv':
            self.tracks = []
            self.kpis = pd.DataFrame(None, columns=[
                'driver_num', 'track_num', 'v', 'a', 'v_r', 'accel'])

            track_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
            files = os.listdir(track_file_path)

            for file_name in random.sample(files, NUM_CSV):
                # ['121.csv', '124.csv', '151.csv', '159.csv']
                # ['55.csv', '108.csv', '115.csv', '106.csv']:
                # ['10.csv', '100.csv', '105.csv', '110.csv', '114.csv']:
                # ['15.csv', '83.csv', '84.csv', '88.csv', '102.csv']
                # random.sample(files, NUM_CSV):
                track_num = int(os.path.splitext(file_name)[0])
                track = Track(driver_num, track_num)
                self.tracks.append(track)
                self.kpis = self.kpis.append(track.kpi, ignore_index=True)

            self.kpis.sort(['driver_num', 'track_num'], inplace=True)
            self.save_kpi()

        else:
            self.load_kpi()

        if len(self.kpis) >= 4:
            self.cluster()

            if method == 'csv':
                self.plot_tracks()
                self.plot_turns()
                self.plot_v()

            self.plot_kpi()
            self.plot_hist()

            file_list = []
            for kpi in self.kpis[self.kpis['probability'] == 0]['track_num']:
                file_list.append("'" + str(int(kpi)) + ".csv', ")
            print ''.join(file_list)

# =============================================================================
    def save_kpi(self):
        """
        Saves KPI data to disk
        """
        self.kpis.to_csv(str(self.driver_num) + '.txt')

# =============================================================================
    def load_kpi(self):
        """
        Loads KPI data from disk
        """
        file_fullname = str(self.driver_num) + '.txt'
        self.kpis = pd.DataFrame.from_csv(file_fullname, index_col=False)

# =============================================================================
    def save_result(self):
        """
        Saves the result to a file for submission
        """
        file_name = 'submission.csv'
        # df = pd.DataFrame.from_csv(file_name, index_col=False)
        # df[['driver_num', 'track_num']] = pd.DataFrame(
        #     df['driver_trip'].str.split('_').tolist(),
        #     columns=['driver_num', 'track_num']
        # )
        # df = df[
        #         df['driver_num'] != self.driver_num
        #         ][['driver_num', 'track_num', 'prob']]

        # df_kpi = self.kpis.copy()
        # df_kpi['driver_trip'] = df_kpi.applymap(
        #     lambda x: str(int(x['driver_num'])) + '_' + str(int(x['track_num']))
        # )

        # df_kpi['prob'] = int(df_kpi['probability'])

        # df = df.append(df_kpi)
        # df.sort(['driver_num', 'track_num'], inplace=True)

        # df[['driver_trip', 'prob']].to_csv(file_name)




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

        columns = ['v', 'a', 'v_r', 'accel']
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
        self.kpis['probability'] = [1 if p == mc else 0 for p in part.tolist()]

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
            print cluster
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
        for track, p in zip(self.tracks, self.kpis['probability']):
            if p == 1 and n_1 < 5:
                n_1 += 1
                track.track_df.plot(x='t', y='v', ax=axes, color='k', ls=':')
            elif p == 0 and n_0 < 5:
                n_0 += 1
                track.track_df.plot(x='t', y='v', ax=axes, color='r', ls=':')

        axes.set_xlim([0, 400])
        axes.set_ylim([0, 40])
        axes.legend().remove()
        sns.despine()
        fig.savefig(str(self.driver_num) + '_v(t)' + EXT)
        plt.close(fig)


# =============================================================================
    def plot_kpi(self):
        """
        Makes a plot of KPI for every track
        """
        print 'Plotting KPI'

        colors = \
            np.where(self.kpis['probability'] == 0, 'red', 'gray').tolist()

        fig, axes = plt.subplots(4, 1)
        for y, axis in zip(['v', 'a', 'v_r', 'accel'], axes):
            self.kpis.plot(x='track_num', y=y,
                           color=colors, kind='bar',
                           ax=axis, title=y)
            axis.legend().remove()

        fig.set_size_inches(20, 13)
        sns.despine()
        fig.savefig(str(self.driver_num) + '_kpi' + EXT)
        plt.close(fig)

# =============================================================================
    def plot_tracks(self):
        """
        Plots all tracks of a driver
        """
        print 'Plotting tracks'

        fig, axes = plt.subplots()
        for track, p in zip(self.tracks, self.kpis['probability']):
            if p == 1:
                track.track_df.plot(x='x', y='y', ax=axes, color='k', ls=':')
            else:
                track.track_df.plot(x='x', y='y', ax=axes, color='r')

        axes.autoscale()
        axes.legend().remove()
        sns.despine()
        fig.savefig(str(self.driver_num) + '_tracks' + EXT)
        plt.close(fig)

# =============================================================================
    def plot_turns(self):
        """
        Plots v(r) for every turn of each track
        """
        print 'Plotting v(r)'

        fig, axes = plt.subplots()
        for track, p in zip(self.tracks, self.kpis['probability']):
            if p == 1:
                track.track_df.plot(x='r', y='v', ax=axes,
                                    ls='', marker='.', color='grey')
            else:
                track.track_df.plot(x='r', y='v', ax=axes,
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
        Plots histograms of KPI's for all tracks
        """
        print 'Plotting histograms'

        fig, axes = plt.subplots()
        self.kpis[['v', 'a', 'v_r', 'accel']].hist(ax=axes, bins=50)
        sns.despine()
        fig.savefig(str(self.driver_num) + '_hist' + EXT)
        plt.close(fig)


# dr = Driver(DRIVER_NUM, method='load')
dr = Driver(DRIVER_NUM, method='csv')
print 'Bad'
print dr.kpis[dr.kpis['bad'] == True]['track_num']

print 'Result'
print dr.kpis[dr.kpis['probability'] == 0][['track_num', 'v', 'a', 'v_r']]

print 'Save result to file'
dr.save_result()

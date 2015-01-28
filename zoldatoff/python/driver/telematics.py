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
import matplotlib.font_manager as fm
import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as dis

from collections import Counter
from pykalman import KalmanFilter


# Откуда и сколько траекторий берём
DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
DRIVER_NUM = 2
NUM_CSV = 10
EXPORT = '.png'

DS_MIN = 1.0          # Минимальное расстояние, для которого считается радиус поворота
VELOCITY_LOW = 5.0    # Участок ускорения отбирается для скоростей из диапазона
VELOCITY_HIGH = 15.0  #       между VELOCITY_LOW и VELOCITY_HIGH
ACCEL_MINLEN = 10.0   # Длина участка разгона не менее ACCEL_MINLEN точек
#ACCEL_HEAD = 5.0     # В начале разгона ускорение завышено - этот участок мы отбрасываем
ACCEL_TAIL = 3        # В конце разгона ускорение снижается - этот участок мы отбрасываем
DISTANCE_MAX = 30.0

ANALYTICS_RADIUS = 30   # Измеряем максимальную скорость вхождения в этот радиус

METHOD = 'single'

COLORS = [
    '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
    '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC'
]

DEBUG = 1



class Track(object):
    """
    This class:
     * reads track data from csv file
     * smooths data using Kalman filter
     * calculates velocity, acceleration and turn radius in every point of the track
     * calculates KPI's for the track

    KPI's include:
     * maximum velocity
     * maximum acceleration
     * maximum velocity in turn with radius < ANALYTICS_RADIUS
     * maximum acceleration on the accelerating parts of the track

    """
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
            self.plot_track()

        if DEBUG >= 2:
            print self.track_df[['t', 'x', 'y', 'ds', 'v', 'a', 'r', 'accel']]



    def cvs_to_df(self):
        """
        Reads track data (x, y) from csv file
        """
        track_file_name = str(self.track_num) + '.csv'
        track_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
        self.track_df = pd.DataFrame.from_csv(track_file_path + track_file_name, index_col=False)


    def df_kalman(self, method='smooth'):
        """
        Smooths track using Kalman method
         * https://github.com/pykalman/pykalman
         * http://pykalman.github.io
         * https://ru.wikipedia.org/wiki/Фильтр_Калмана
         * http://www.hdm-stuttgart.de/~maucher/Python/ComputerVision/html/Tracking.html
        """
        df = self.track_df

        # Plot beginning
        if DEBUG >= 1:
            fig, axes = plt.subplots()
            df.plot(x='x', y='y', ax=axes, ls='-', marker='.', color='k', title='original')

        # pylint: disable=E1103
        df['ds'] = np.sqrt(
            np.square(df['x'] - df['x'].shift(1))
            +
            np.square(df['y'] - df['y'].shift(1))
        )

        # Маскируем ошибочные точки
        df['x'] = np.where(df['ds'] > DISTANCE_MAX, np.ma.masked, df['x'])
        df['y'] = np.where(df['ds'] > DISTANCE_MAX, np.ma.masked, df['y'])
        # pylint: enable=E1103

        # Фильтр Кальмана
        kf = KalmanFilter(\
            transition_matrices = [[1, 0], [0, 1]],\
            observation_matrices = [[1, 0], [0, 1]]
        )
        measurements = df[['x', 'y']].values
        kf = kf.em(measurements, n_iter=5)

        if method == 'filter':
            (state_means, state_covariances) = kf.filter(measurements)
        elif method == 'smooth':
            (state_means, state_covariances) = kf.smooth(measurements)

        kalman_df = pd.DataFrame(state_means, columns=('x', 'y'))

        # Plot continue
        if DEBUG >= 1:
            kalman_df.plot(x='x', y='y', ax=axes, ls='-', marker='.', color='r', title='Kalman')
            axes.autoscale()
            axes.legend().remove()
            fig.savefig(str(self.driver_num) + '_' + str(self.track_num) + '_' + method + EXPORT)


        self.track_df['x'] = kalman_df['x']
        self.track_df['y'] = kalman_df['y']


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
        # pylint: disable=E1103
        df['ds'] = np.sqrt(
            np.square(df['x'] - df['x'].shift(1))
            +
            np.square(df['y'] - df['y'].shift(1))
        )

        # скорость
        df['v'] = df['ds'] / df['dt']

        # ускорение
        df['a'] = (df['v'] - df['v'].shift(1)) / df['dt']

        # направление движения
        df['ang'] = np.where(
            df['ds'] > DS_MIN,
            np.arctan2(
                df['y'] - df['y'].shift(1),
                df['x'] - df['x'].shift(1)
            ),
            None
        )

        # смена направления движения
        df['dang'] = df['ang'] - df['ang'].shift(1)
        df['dang'] = df['dang'].apply(lambda x: x - 2.0*np.pi if x > np.pi else x)
        df['dang'] = df['dang'].apply(lambda x: x + 2.0*np.pi if x < -np.pi else x)

        # pylint: enable=E1103

        # радиус поворота
        df['r'] = \
            (df['ds'] + df['ds'].shift(1)) / 2.0 / (abs(df['dang']) + 0.000001)


        self.track_df = df



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

            elif len(accel) > 0 and VELOCITY_LOW < curr['v'] and (curr['a'] > 0.0 or prev['a'] > 0.0):
                accel.add(curr['t'])

            elif len(accel) > ACCEL_MINLEN and curr['a'] < 0.0 and prev['a'] < 0.0:
                n += 1
                self.track_df.ix[self.track_df['t'].isin(accel), 'accel'] = n
                accel.clear()

            else:
                accel.clear()

            prev = curr



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


    def key_indicator(self):
        """
        Defines KPI's for the driver:
         * maximum velocity
         * maximum acceleration
         * maximum velocity in turn with radius < ANALYTICS_RADIUS
         * maximum acceleration on the accelerating parts of the track
        """
        kpi = {'driver_num': self.driver_num, 'track_num': self.track_num}

        df = self.track_df[self.track_df['v'] > 0.0]
        kpi['v'] = self.decile(df, 'v')
        #print 'v=', kpi['v']

        df = self.track_df[self.track_df['a'] > 0.0]
        kpi['a'] = self.decile(df, 'a')
        #print 'a=', kpi['a']

        df = self.track_df[self.track_df['r'] <= ANALYTICS_RADIUS]
        kpi['v_r'] = self.decile(df, 'v')
        #print 'v_r=', kpi['v_r']

        df = self.track_df[self.track_df['accel'] > 0]
        kpi['accel'] = self.decile(df, 'a')
        #print 'accel=', kpi['accel']

        self.kpi = kpi


    def plot_track(self):
        """
        Makes a plot v(t) for one particuls track and shows acceleration parts
        """
        fig, axes = plt.subplots()
        m = self.track_df['accel'].max()

        for i in range(m+1):
            df = self.track_df[self.track_df['accel']==i]
            if i == 0:
                df.plot(x='t', y='v', ax=axes, ls='', marker='.', color='k')
            else:
                df.plot(x='t', y='v', ax=axes, ls='--', marker='.', color='r')

        axes.autoscale()
        axes.legend().remove()
        #axes.set_xlim([0, 100])
        fig.savefig(str(self.driver_num) + '_' + str(self.track_num) + '_v(t)' + EXPORT)



class Driver(object):
    """
    Driver is a class that contains:
     * tracks data
     * method for clustering KPI's
     * methods for data visualization
    """
    def __init__(self, driver_num=1, method='csv'):
        """
        Loads track (or KPI) data from files
        """
        self.driver_num = driver_num

        if method == 'csv':
            self.tracks = []
            self.kpis = pd.DataFrame(None, columns=['driver_num', 'track_num', 'v', 'a', 'v_r', 'accel'])

            track_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
            files = os.listdir(track_file_path)

            for file_name in random.sample(files, NUM_CSV): #['55.csv']: #random.sample(files, NUM_CSV):
                track_num = int(os.path.splitext(file_name)[0])
                track = Track(driver_num, track_num)
                self.tracks.append(track)
                self.kpis = self.kpis.append(track.kpi, ignore_index=True)

            self.kpis = self.kpis.sort(['driver_num', 'track_num'])
            self.kpis.fillna(0, inplace=True)

            self.save()
        else:
            self.load()


        self.cluster()

        if method == 'csv':
            self.plot_tracks()
            self.plot_turns()


        self.plot_kpi()
        self.plot_hist()


    def save(self):
        """
        Saves KPI data to disk
        """
        self.kpis.to_csv(str(self.driver_num) + '.txt')


    def load(self):
        """
        Loads KPI data to disk
        """
        file_fullname = str(self.driver_num) + '.txt'
        self.kpis = pd.DataFrame.from_csv(file_fullname, index_col=False)


    def cluster(self):

        med_v, med_a, med_v_r, med_accel = \
            self.kpis['v'].median(), self.kpis['a'].median(), self.kpis['v_r'].median(), self.kpis['accel'].median()
        self.kpis['v'] *= med_v_r / med_v
        self.kpis['a'] *= med_v_r / med_a
        self.kpis['accel'] *= med_v_r / med_accel


        matr = self.kpis.as_matrix(columns=['v', 'a', 'v_r', 'accel'])
        a = dis.squareform(dis.pdist(matr))


        z = hac.linkage(a, method=METHOD)
        knee = np.diff(z[::-1, 2], 2)

        num_clust = knee.argmax() + 2
        part = hac.fcluster(z, num_clust, 'maxclust')


        mc = Counter(part).most_common(1)[0][0]
        self.kpis['probability'] = [1 if p == mc else 0 for p in part.tolist()]


        self.plot_cluster(a, z, knee, num_clust, part, self.driver_num)


    @staticmethod
    def plot_cluster(a, z, knee, num_clust, part, driver_num):
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
        for cluster in set(part):
            axes[1].scatter(a[part == cluster, 0], a[part == cluster, 1], color=COLORS[cluster])
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

        #plt.tight_layout()
        fig.set_size_inches(20, 5)
        plt.savefig(str(driver_num) + '_cluster' + EXPORT)


    def plot_kpi(self):

        colors = np.where(self.kpis['probability'] == 0, 'red', 'gray').tolist()

        fig, axes = plt.subplots(4, 1)
        self.kpis.plot(x='track_num', y='v', color=colors, kind='bar', ax=axes[0], title='v')
        self.kpis.plot(x='track_num', y='a', color=colors, kind='bar', ax=axes[1], title='a')
        self.kpis.plot(x='track_num', y='v_r', color=colors, kind='bar', ax=axes[2], title='vr')
        self.kpis.plot(x='track_num', y='accel', color=colors, kind='steps', ax=axes[3], title='accel')
        axes[0].legend().remove()
        axes[1].legend().remove()
        axes[2].legend().remove()
        fig.set_size_inches(20, 13)
        fig.savefig(str(self.driver_num) + '_kpi' + EXPORT)



    def plot_tracks(self):
        """
        Plots all tracks of a driver
        """
        fig, axes = plt.subplots()
        for track, p in zip(self.tracks, self.kpis['probability']):
            if p == 1:
                track.track_df.plot(x='x', y='y', ax=axes, ls=':', color='k')
            else:
                track.track_df.plot(x='x', y='y', ax=axes, color='r')

        axes.autoscale()
        axes.legend().remove()
        fig.savefig(str(self.driver_num) + '_tracks' + EXPORT)



    def plot_turns(self):
        fig, axes = plt.subplots()
        for track, p in zip(self.tracks, self.kpis['probability']):
            if p == 1:
                track.track_df.plot(x='r', y='v', ax=axes, ls='', marker='.', color='grey')
            else:
                track.track_df.plot(x='r', y='v', ax=axes, ls='', marker='.', color='red')

        axes.legend().remove()
        axes.set_xlim([0, 50])
        axes.set_ylim([0, 15])
        fig.savefig(str(self.driver_num) + '_turns' + EXPORT)


    def plot_hist(self):
        self.kpis[['v', 'a', 'v_r', 'accel']].hist(bins=50) #analytics.plot(x='n')
        plt.savefig(str(self.driver_num) + '_hist' + EXPORT)



for dr in [1]:
    dr = Driver(dr)

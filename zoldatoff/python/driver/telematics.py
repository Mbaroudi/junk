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


# Откуда и сколько траекторий берём
DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
DRIVER_NUM = 2
NUM_CSV = 50
EXPORT = '.eps'

DS_MIN = 2.0          # Минимальное расстояние, для которого считается радиус поворота
VELOCITY_LOW = 5.0    # Участок ускорения отбирается для скоростей из диапазона
VELOCITY_HIGH = 15.0  #       между VELOCITY_LOW и VELOCITY_HIGH
ACCEL_MINLEN = 15.0   # Длина участка разгона не менее ACCEL_MINLEN точек
#ACCEL_HEAD = 5.0     # В начале разгона ускорение завышено - этот участок мы отбрасываем
ACCEL_TAIL = 3        # В конце разгона ускорение снижается - этот участок мы отбрасываем

ANALYTICS_RADIUS = 30   # Измеряем максимальную скорость вхождения в этот радиус

METHOD = 'single'

COLORS = [
        '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
        '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
        '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
        '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC',
        ##
        '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
        '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
        '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
        '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC',
        ##
        '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
        '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
        '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
        '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC']


class Track:
    def __init__(self, driver_num, track_num):
        self.driver_num = driver_num
        self.track_num = track_num

        track_file_name = str(self.track_num) + '.csv'
        track_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
        self.track_df = self.cvs_to_df(track_file_path + track_file_name)

        self.kpi = self.key_indicator(self.track_df)

        #print self.track_df
        #print self.kpi
        print 'Driver =', str(self.driver_num), ', track =', str(self.track_num)

    @staticmethod
    def cvs_to_df(file_fullname):
        track_df = pd.DataFrame.from_csv(file_fullname, index_col=False)

        # pylint: disable=E1103

        # время
        track_df['t'] = track_df.index

        # дельта времени
        track_df['dt'] = track_df['t'] - track_df['t'].shift(1)

        # расстояние
        track_df['ds'] = np.sqrt(
            np.square(track_df['x'] - track_df['x'].shift(1))
            +
            np.square(track_df['y'] - track_df['y'].shift(1))
        )

        # скорость
        track_df['v'] = track_df['ds'] / track_df['dt']

        # ускорение
        track_df['a'] = (track_df['v'] - track_df['v'].shift(1)) / track_df['dt']

        # направление движения
        track_df['ang'] = np.where(
            track_df['ds'] > DS_MIN,
            np.arctan2(
                track_df['y'] - track_df['y'].shift(1),
                track_df['x'] - track_df['x'].shift(1)
            ),
            None
        )

        # смена направления движения
        track_df['dang'] = track_df['ang'] - track_df['ang'].shift(1)
        track_df['dang'] = track_df['dang'].apply(lambda x: x - 2.0*np.pi if x > np.pi else x)
        track_df['dang'] = track_df['dang'].apply(lambda x: x + 2.0*np.pi if x < -np.pi else x)

        # радиус поворота
        track_df['r'] = \
            (track_df['ds'] + track_df['ds'].shift(1)) / 2.0 / (abs(track_df['dang']) + 0.000001)

        # pylint: enable=E1103

        return track_df


    @staticmethod
    def key_indicator(track_df):
        kpi = {}

        # минимальное значение скорости из верхней децили
        #df = track_df[track_df['v'] > 0.0]
        track_df['decile'] = pd.qcut(track_df['v'], [0.0, 0.91, 1.0], labels=False)
        kpi['v'] = track_df[track_df['decile'] == 1]['v'].min()

        # минимальное значение ускорения из верхней децили
        #df = track_df[track_df['a'] > 0.0]
        #kpi['a'] = df.sort('a', ascending=1)['a'].tolist()[2]
        track_df['decile'] = pd.qcut(track_df['a'], [0.0, 0.91, 1.0], labels=False)
        kpi['a'] = track_df[track_df['decile'] == 1]['a'].min()

        # максимальная скорость прохождения поворота с радиусом <= ANALYTICS_RADIUS
        kpi['v_r'] = track_df[track_df['r'] <= ANALYTICS_RADIUS]['v'].max()

        return kpi



class Driver:
    def __init__(self, driver_num):
        self.driver_num = driver_num
        self.tracks = []
        self.kpis = pd.DataFrame(None, columns=['driver_num', 'track_num', 'v', 'a', 'v_r'])

        track_file_path = DATA_PATH + '/' + str(self.driver_num) + '/'
        files = os.listdir(track_file_path)

        for file_name in files: #random.sample(files, NUM_CSV):
            track_num = int(os.path.splitext(file_name)[0])
            track = Track(driver_num, track_num)
            self.tracks.append(track)

            kpi = track.kpi
            kpi['driver_num'] = track.driver_num
            kpi['track_num'] = track.track_num
            self.kpis = self.kpis.append(kpi, ignore_index=True)

        self.kpis = self.kpis.sort(['driver_num', 'track_num'])
        self.kpis.fillna(0, inplace=True)

        self.cluster(self.kpis)

        #print self.kpis


    def save(self):
        self.kpis.to_csv(str(self.driver_num) + '.txt')


    def load(self, driver_num):
        file_fullname = str(self.driver_num) + '.txt'
        self.kpis = pd.DataFrame.from_csv(file_fullname, index_col=False)


    @staticmethod
    def cluster(kpis):

        driver_num = int(kpis['driver_num'][0])

        med_v, med_a, med_v_r = kpis['v'].median(), kpis['a'].median(), kpis['v_r'].median()
        kpis['v'] *= med_v_r / med_v
        kpis['a'] *= med_v_r / med_a


        matr = kpis.as_matrix(columns=['a', 'v', 'v_r'])

        a = dis.squareform(dis.pdist(matr))

        fig, axes = plt.subplots(1, 3)

        z = hac.linkage(a, method=METHOD)
        knee = np.diff(z[::-1, 2], 2)
        num_clust = knee.argmax() + 2
        part = hac.fcluster(z, num_clust, 'maxclust')

        mc = Counter(part).most_common(1)[0][0]
        #TODO Надо вернуть эту информацию элементу класса
        kpis['probability'] = [1 if p==mc else 0 for p in part.tolist()]


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

        for cluster in set(part):
            axes[1].scatter(a[part==cluster, 0], a[part==cluster, 1], color=COLORS[cluster])
        axes[1].grid()

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
        fig.set_size_inches(20,5)
        plt.savefig(str(driver_num) + '_analytics' + EXPORT)


        # Plot #2
        colors = np.where(kpis['probability']==0, 'red', 'gray').tolist()

        fig, axes = plt.subplots(3, 1)
        kpis.plot(x='track_num', y='v', color=colors, kind='bar', ax=axes[0], title='v')
        kpis.plot(x='track_num', y='a', color=colors, kind='bar', ax=axes[1], title='a')
        kpis.plot(x='track_num', y='v_r', color=colors, kind='bar', ax=axes[2], title='vr')
        axes[0].legend().remove()
        axes[1].legend().remove()
        axes[2].legend().remove()
        fig.set_size_inches(20,10)
        fig.savefig(str(driver_num) + '_result' + EXPORT)







for dr in [1,2,3]:
    dr = Driver(dr)
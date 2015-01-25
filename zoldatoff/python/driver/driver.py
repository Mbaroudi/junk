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

import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as dis

# Откуда и сколько траекторий берём
DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
DRIVER_NUM = 2
NUM_CSV = 50

VELOCITY_LOW = 5    # Участок ускорения отбирается для скоростей из диапазона
VELOCITY_HIGH = 15  #       между VELOCITY_LOW и VELOCITY_HIGH
ACCEL_MINLEN = 15   # Длина участка разгона не менее ACCEL_MINLEN точек
#ACCEL_HEAD = 5     # В начале разгона ускорение завышено - этот участок мы отбрасываем
ACCEL_TAIL = 3      # В конце разгона ускорение снижается - этот участок мы отбрасываем

ANALYTICS_RADIUS = 30   # Измеряем максимальную скорость вхождения в этот радиус



def csv2dataframe(filename=DATA_PATH + '/' + str(DRIVER_NUM) + '/1.csv'):
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
        data['ds'] > 0.2,
        np.arctan2(
            data['y']-data['y'].shift(1),
            data['x']-data['x'].shift(1)
        ),
        None
    )

    data['dang'] = data['ang'] - data['ang'].shift(1)                   # смена направления движения
    data['dang'] = data['dang'].apply(lambda x: x - 2.0*np.pi if x > 4.0 else x)
    data['dang'] = data['dang'].apply(lambda x: x + 2.0*np.pi if x < -4.0 else x)

    # радиус поворота
    data['r'] = (data['ds'] + data['ds'].shift(1)) / (abs(data['dang']) + 0.000001) / 2.0
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
            accel_df = pd.DataFrame(accel, columns=['t', 'v', 'a'])
            accel_all.append(accel_df[0:-ACCEL_TAIL])
            accel = []

        else:
            accel = []

        prev = curr

    return accel_all



def dataframe2analytics(n, dataframe):
    dataframe['decile_v'] = pd.qcut(dataframe['v'], [0.0, 0.91, 1.0], labels=False)
    analytics_v = dataframe[dataframe['decile_v']==1][['v']].min()[0]

    dataframe['decile_a'] = pd.qcut(dataframe['a'], [0.0, 0.91, 1.0], labels=False)
    analytics_a = dataframe[dataframe['decile_a']==1][['a']].min()[0]

    analytics_v_r = dataframe[dataframe['r']<=ANALYTICS_RADIUS][['v']].max()[0]

    return pd.DataFrame({'n': n, 'v': analytics_v, 'a': analytics_a, 'v_r': analytics_v_r}, columns=['n', 'v', 'a', 'v_r'], index=['n'])


def analytics2clusters(analytics):
    print analytics
    matr = analytics.as_matrix(columns=['a', 'v', 'v_r'])
    a = dis.squareform(dis.pdist(matr))

    fig, axes73 = plt.subplots(7, 3)

    for method, axes in zip(['single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward'], axes73):
    # 'single', 'complete', 'average', 'weighted', 'centroid', 'median', 'ward'
        z = hac.linkage(a, method=method)
        #hac.dendrogram(z, ax=axes[3])

        # Plotting
        axes[0].plot(range(1, len(z)+1), z[::-1, 2])
        knee = np.diff(z[::-1, 2], 2)
        axes[0].plot(range(2, len(z)), knee)

        num_clust1 = knee.argmax() + 2
        knee[knee.argmax()] = 0
        num_clust2 = knee.argmax() + 2

        print num_clust1, num_clust2

        axes[0].text(num_clust1, z[::-1, 2][num_clust1-1], 'possible\n<- knee point')

        part1 = hac.fcluster(z, num_clust1, 'maxclust')
        part2 = hac.fcluster(z, num_clust2, 'maxclust')

        clr = [ '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
                '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
                '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
                '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC',
                ##
                '#2200CC', '#D9007E', '#FF6600', '#FFCC00', '#ACE600', '#0099CC',
                '#8900CC', '#FF0000', '#FF9900', '#FFFF00', '#00CC01', '#0055CC',
                '#2288CC', '#D9887E', '#FF6688', '#FFCC88', '#ACE688', '#8899CC',
                '#8988CC', '#FF8800', '#FF9988', '#FFFF88', '#88CC01', '#8855CC']

        for part, ax in zip([part1, part2], axes[1:]):
            for cluster in set(part):
                ax.scatter(a[part == cluster, 0], a[part == cluster, 1],
                           color=clr[cluster])

        m = '\n(method: {})'.format(method)
        plt.setp(axes[0], title='Screeplot{}'.format(m), xlabel='partition',
                 ylabel='{}\ncluster distance'.format(m))
        plt.setp(axes[1], title='{} Clusters'.format(num_clust1))
        plt.setp(axes[2], title='{} Clusters'.format(num_clust2))

    #plt.tight_layout()
    fig.set_size_inches(20,40)
    plt.savefig('analytics.png')



def plot_stats():
    """
    Make plots as in this article: http://cs229.stanford.edu/proj2013/DriverIdentification.pdf
    'Driver Identification by Driving Style'
    """

    path = DATA_PATH + '/' + str(DRIVER_NUM) + '/'
    files = os.listdir(path)

    analytics = pd.DataFrame(None, columns=['n', 'v', 'a', 'v_r'])

    for file_name in files: # random.sample(files, NUM_CSV):
        n, e = ( x for x in os.path.splitext(file_name) )

        driver_data = csv2dataframe(path + file_name)

        analytics = analytics.append(dataframe2analytics(int(n), driver_data))

        accel_all = extract_accel(driver_data)

        # accel_a = []

        # for accel in accel_all:
        #     plt.figure(4)
        #     accel['v'].plot()

        #     accel_a.append(accel['a'].mean())

        # plt.figure(5)
        # if accel_a:
        #     plt.hist(accel_a, range=(0, 5), bins=40, normed=True)

        # fig = plt.figure(1)
        # driver_data.plot(x='x', y='y', ls='--', ax=fig.gca()) #color='red', markerfacecolor='red',

        # plt.figure(2)
        # driver_data['v'].hist(bins=40, normed=True)

        # plt.figure(3)
        # driver_data['a'].hist(bins=40, normed=True)

        # fig = plt.figure(6)
        # driver_data.plot(x='r', y='v', ls='', marker='.', ax=fig.gca())

        # fig = plt.figure(8)
        # driver_data.plot(x='t', y='v', ax=fig.gca())

        print 'driver =', DRIVER_NUM, 'file =', file_name, ' accel_cnt = ', len(accel_all)

    analytics = analytics.sort('n')
    analytics['a'] = 15.0 * analytics['a']
    analytics2clusters(analytics)

    # plt.figure(1)
    # plt.autoscale()
    # plt.legend().remove()
    # plt.savefig(str(DRIVER_NUM) + '. trajectory.eps')

    # plt.figure(2)
    # plt.xlim([1, 45])
    # plt.ylim([0, 0.5])
    # plt.savefig(str(DRIVER_NUM) + '. v(hist).eps')

    # plt.figure(3)
    # plt.xlim([0.2, 6])
    # plt.ylim([0, 1])
    # plt.savefig(str(DRIVER_NUM) + '. a(hist).eps')

    # plt.figure(4)
    # plt.xlim([0, 45])
    # plt.ylim([0, 30])
    # plt.savefig(str(DRIVER_NUM) + '. accel v(t).eps')

    # plt.figure(5)
    # plt.xlim([0.01, 4])
    # plt.ylim([0, 10])
    # plt.savefig(str(DRIVER_NUM) + '. accel mean(a).eps')

    # plt.figure(6)
    # plt.legend().remove()
    # plt.xlim([0, 50])
    # plt.ylim([0, 15])
    # plt.savefig(str(DRIVER_NUM) + '. v(r).eps')

    # plt.figure(8)
    # plt.legend().remove()
    # plt.xlim([0, 500])
    # plt.ylim([0, 50])
    # plt.savefig(str(DRIVER_NUM) + '. v(t).eps')

    plt.figure(9)
    analytics[['v', 'a', 'v_r']].hist(bins=50) #analytics.plot(x='n')
    plt.savefig(str(DRIVER_NUM) + '. analytics.eps')


plot_stats()

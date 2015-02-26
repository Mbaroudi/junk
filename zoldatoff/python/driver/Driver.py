#!/usr/bin/env python
# coding: utf-8

import Trip

import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import scipy.cluster.hierarchy as hac
import scipy.spatial.distance as dis

from sklearn.decomposition import PCA
from sklearn import preprocessing

from collections import Counter

# Откуда и сколько траекторий берём
DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
KPI_PATH = './kpi/'
PLOT_EXT = '.eps'
# NUM_TRIP = 10
METHOD = 'single'

# Google Chart Color List
# http://there4development.com/blog/2012/05/02/google-chart-color-list/
COLORS = [
    '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#3B3EAC',
    '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395', '#994499',
    '#22AA99', '#AAAA11', '#6633CC', '#E67300', '#8B0707', '#329262',
    '#5574A6', '#3B3EAC'] * 20


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
            self.cluster()
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
    def cluster(self):
        """
        Scales and clusters KPI data
        http://stackoverflow.com/questions/21638130/tutorial-for-scipy-cluster-hierarchy
        """

        # 'vR', 's', 'a', 'accel', 'decel', 'calm', 'nerv_a', 'nerv_ang'
        columns = ['accel', 'nerv_a']
        kpis = self.kpis[columns]
        a = kpis.as_matrix(columns=columns)

        min_max_scaler = preprocessing.MinMaxScaler()
        a = min_max_scaler.fit_transform(a)
        # a = preprocessing.scale(a)
        # kpis[columns].fillna(0.5, inplace=True)

        print a
        z = hac.linkage(dis.pdist(a), method=METHOD)
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

        columns = ['vR', 's', 'a', 'accel', 'decel',
                   'calm', 'nerv_a', 'nerv_ang']
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

        fig, axes = plt.subplots(9, 1)
        for y, axis in zip(
                ['vR', 's', 'a', 'accel', 'decel',
                 'calm', 'nerv_a', 'nerv_ang'],
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
            color_num = [1 for i in range(1, 21)] \
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

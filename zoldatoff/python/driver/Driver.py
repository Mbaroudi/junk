#!/usr/bin/env python
# coding: utf-8

import Trip
from Const import *

import random
import os
import pandas as pd
import matplotlib.pyplot as plt

NUM_TRIP = 200


class Driver(object):
    """
    Driver is a class that contains:
     * trips data
     * method for clustering KPI's
     * methods for data visualization
    """
    def __init__(self, driver_num=1):
        """
        Loads trip (or KPI) data from files
        """
        self.driver_num = driver_num

        self.get_data()
        self.save_kpi()

        if DEBUG >= 1:
            self.plot_rv()
            self.plot_kpi()
            self.plot_trips()
            print self.kpis

    # =========================================================================
    def get_data(self):
        """
        Считывае параметры (KPI) всех траекторий водителя
        """
        self.trips = []
        self.kpis = pd.DataFrame(None)

        trip_file_path = DRIVER_PATH + '/' + str(self.driver_num) + '/'
        files = os.listdir(trip_file_path)
        trips = [int(os.path.splitext(f)[0]) for f in files]

        if DEBUG >= 1:
            trips = random.sample(trips, NUM_TRIP)

        for trip_num in sorted(trips):
            trip = Trip.Trip(self.driver_num, trip_num)
            self.trips.append(trip)
            self.kpis = self.kpis.append(trip.kpi, ignore_index=True)

        self.kpis.sort(['driver_num', 'trip_num'], inplace=True)

    # =========================================================================
    def save_kpi(self):
        """
        Saves KPI data to disk
        """
        self.kpis.to_csv(KPI_PATH + str(self.driver_num) + '.txt',
                         index=False,
                         sep='\t')

    # =========================================================================
    def plot_kpi(self):
        """
        Makes a plot of KPI for every trip
        """
        print 'Plotting KPI'

        fig, axes = plt.subplots(len(COL), 1)
        for y, axis in zip(COL, axes):
            self.kpis.plot(x='trip_num', y=y,
                           color='gray', kind='bar',
                           ax=axis, title=y)
            axis.legend().remove()

        fig.set_size_inches(15, 10)
        fig.savefig(PLOT_PATH + str(self.driver_num) + '_kpi' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_rv(self):
        """
        Plots v(r) for every turn of each trip
        """
        print 'Plotting v(r)'

        fig, axes = plt.subplots()
        for trip in self.trips:
            df = trip.trip_data
            df = df[(df.flag_turn_left == 1) | (df.flag_turn_right == 1)]
            if not df.empty:
                df.plot(x='r', y='v', ax=axes,
                        ls='', marker='.', color='grey')

        axes.legend().remove()
        axes.set_xlim([0, 50])
        axes.set_ylim([0, 15])

        fig.savefig(PLOT_PATH + str(self.driver_num) + '_vR' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_trips(self):
        """
        Plots all trips of a driver
        """
        print 'Plotting trips'

        fig, axes = plt.subplots()
        i = 0
        for trip in self.trips:
            trip.trip_data.plot(x='x', y='y', ax=axes, color=COLORS[i])
            i += 1

        axes.autoscale()
        plt.axis('equal')
        axes.legend().remove()
        fig.savefig(PLOT_PATH + str(self.driver_num) + '_trips' + PLOT_EXT)
        plt.close(fig)

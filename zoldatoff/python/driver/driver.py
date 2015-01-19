#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
SHIFT_LEN = 10
BINS_NUM = 20


def plot_driver():
    num_plots = 30

    labels = []

    for i in range(num_plots):
        print(i)

        driver_data = pd.DataFrame.from_csv(DATA_PATH + '/1/' + str(i+1) + '.csv', index_col=False)

        driver_data['t'] = driver_data.index
        driver_data['dt'] = driver_data['t'] - driver_data['t'].shift(SHIFT_LEN)
        driver_data['ds'] = np.sqrt(
            np.square(driver_data['x'] - driver_data['x'].shift(SHIFT_LEN))
            + np.square(driver_data['y'] - driver_data['y'].shift(SHIFT_LEN))
            )
        driver_data['v'] = driver_data['ds'] / driver_data['dt']
        driver_data['a'] = (driver_data['v'] - driver_data['v'].shift(SHIFT_LEN)) / driver_data['dt']
        
        # Velocity
        plt.figure(1)
        dr_data = driver_data[ (driver_data['v'] > 2.0) & (driver_data['v'] < 50.0)]['v']
        if dr_data.count() > 1.0:
            dr_data.hist(bins=BINS_NUM, histtype='step') # normed=True, histtype='step'

        # Acceleration
        plt.figure(2)
        dr_data = driver_data[ (abs(driver_data['a']) > 0.2) & (abs(driver_data['a']) < 5.0) ]['a']
        if dr_data.count() > 1.0:
            dr_data.hist(bins=BINS_NUM, histtype='step')

        # Trajectory
        fig=plt.figure(3)
        driver_data.plot(x='x', y='y', ax=fig.gca(), ls='--')

        labels.append(str(i+1))


    plt.figure(1)
    plt.legend(labels, ncol=3, loc='upper right', fontsize=7)
    plt.autoscale()
    plt.savefig('velocity.eps')

    plt.figure(2)
    plt.legend(labels, ncol=3, loc='upper right', fontsize=7)
    plt.autoscale()
    plt.savefig('acceleration.eps')

    plt.figure(3)
    plt.legend().remove()
    #plt.legend(labels, ncol=3, loc='upper right', fontsize=7)
    plt.autoscale()
    plt.savefig('trajectory.eps')

plot_driver()

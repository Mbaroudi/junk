#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'
SHIFT_LEN = 3
BINS_NUM = 20

VELOCITY_LOW = 1
VELOCITY_HIGH = 15
ACCEL_MINLEN = 15

NUM_CSV = 10

def csv2dataframe(filename=DATA_PATH + '/1/1.csv'):
    data = pd.DataFrame.from_csv(filename, index_col=False)

    data['t'] = data.index
    data['dt'] = data['t'] - data['t'].shift(SHIFT_LEN)
    data['ds'] = sum([
        np.sqrt(
            np.square(data['x'] - data['x'].shift(shift+1))
            + 
            np.square(data['y'] - data['y'].shift(shift+1))
        )
        for shift in range(SHIFT_LEN)
    ])
    data['v'] = data['ds'] / data['dt']
    data['a'] = (data['v'] - data['v'].shift(SHIFT_LEN)) / data['dt']

    return data


def extract_accel(data):
    #print data

    accel_all = []
    accel = []

    row_iterator = data.iterrows()
    prev = row_iterator.next() 

    n = 1

    for i, curr in row_iterator:
        #print '---'
        #print 'i =', i, ' v =', curr['v'], ', a =', curr['a'] #, ' prev_a =', prev['a']
        #print 'len(accel) =', len(accel)

        if len(accel) == 0 and VELOCITY_LOW < curr['v'] < VELOCITY_HIGH:
            #print '1. append'
            accel.append(curr['v'])

        elif len(accel) > 0 and VELOCITY_LOW < curr['v'] and (curr['a'] > 0.0 or prev['a'] > 0.0):
            #print '2. append'
            accel.append(curr['v'])

        elif len(accel) > ACCEL_MINLEN and curr['a'] < 0.0 and prev['a'] < 0.0:
            #print '3. write'
            accel_all.append(pd.DataFrame(accel, columns=[n]))
            #print pd.DataFrame(accel)
            accel = []
            n+=1

        else:
            #print '4. truncate'
            accel = []

        prev = curr

    return accel_all



def plot_driver():

    labels = []

    fig = plt.figure()

    for i in range(NUM_CSV):
        driver_data = csv2dataframe(DATA_PATH + '/10/' + str(i+1) + '.csv')

        accel_all = extract_accel(driver_data)

        for accel in accel_all:        
            accel.plot(ax=fig.gca())

        print 'traj =', i, ' accel_cnt = ', len(accel_all)


    #     # Velocity
    #     plt.figure(1)
    #     dr_data = driver_data[ (driver_data['v'] > 2.0) & (driver_data['v'] < 50.0)]['v']
    #     if dr_data.count() > 1.0:
    #         dr_data.hist(bins=BINS_NUM, histtype='step') # normed=True, histtype='step'

    #     # Acceleration
    #     plt.figure(2)
    #     dr_data = driver_data[ (abs(driver_data['a']) > 0.2) & (abs(driver_data['a']) < 5.0) ]['a']
    #     if dr_data.count() > 1.0:
    #         dr_data.hist(bins=BINS_NUM, histtype='step')

    #     # Trajectory
    #     fig=plt.figure(3)
    #     driver_data.plot(x='x', y='y', ax=fig.gca(), ls='--')

    #     labels.append(str(i+1))

    plt.autoscale()
    plt.legend(ncol=3, loc='lower right', fontsize=7)
    plt.savefig('behavior.eps')

    # plt.figure(1)
    # plt.legend(labels, ncol=3, loc='upper right', fontsize=7)
    # plt.autoscale()
    # plt.savefig('velocity.eps')

    # plt.figure(2)
    # plt.legend(labels, ncol=3, loc='upper right', fontsize=7)
    # plt.autoscale()
    # plt.savefig('acceleration.eps')

    # plt.figure(3)
    # plt.legend().remove()
    # #plt.legend(labels, ncol=3, loc='upper right', fontsize=7)
    # plt.autoscale()
    # plt.savefig('trajectory.eps')

plot_driver()

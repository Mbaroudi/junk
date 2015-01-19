#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = '/Users/zoldatoff/Downloads/driver/data/'


def plot_driver():
    num_plots = 15

    labels = []

    fig = plt.figure(figsize=(30, 10)) 
    axes = [fig.add_subplot(1, 3, i+1) for i in range(3)]

    for i in range(num_plots):
        driver_data = pd.DataFrame.from_csv(DATA_PATH + '/1/' + str(i+1) + '.csv', index_col=False)
        driver_data['t'] = driver_data.index
        driver_data['dt'] = driver_data['t'] - driver_data['t'].shift(1)
        driver_data['ds'] = np.sqrt(
            np.square(driver_data['x'] - driver_data['x'].shift(1))
            + np.square(driver_data['y'] - driver_data['y'].shift(1))
            )
        driver_data['v'] = driver_data['ds'] / driver_data['dt']
        driver_data['a'] = (driver_data['v'] - driver_data['v'].shift(1)) / driver_data['dt']
        
        driver_data['v'].hist(ax=axes[0], bins=30)
        driver_data['a'].hist(ax=axes[1], bins=30)
        driver_data.plot(x='x', y='y', ls='--', ax=axes[2])
        labels.append(str(i+1))


    axes[2].legend(labels, ncol=3, loc='upper right', fontsize=7)
    
    for axis in axes:
        axis.autoscale()

    fig.savefig('driver.eps')

plot_driver()

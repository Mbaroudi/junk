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

import Trip
# import Driver

import os
import random

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from sklearn.decomposition import PCA
from sklearn import preprocessing
from sklearn import svm
from sklearn.metrics import zero_one_loss
# from sklearn.metrics import classification_report

from nolearn.dbn import DBN


# Откуда и сколько траекторий берём
DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
KPI_PATH = './kpi/'
PLOT_EXT = '.eps'
TRAIN_SIZE = 5

# ['accel', 'decel', 'calm', 'nerv_a', 'nerv_ang', 's', 'vR']
col = ['accel', 'decel', 'calm', 'nerv_a', 'nerv_ang', 's', 'vR']


# =============================================================================
def get_train_data(files, main_driver=1):
    """
    Reads data for training
    http://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html
    """
    # print 'Reading Data for driver', main_driver

    TRAIN_SIZE = 5
    main_file = [KPI_PATH + f for f in files
                 if int(os.path.splitext(f)[0]) == main_driver][0]
    train_files = [KPI_PATH + f for f in random.sample(files, TRAIN_SIZE)
                   if f != main_file]

    # print 'Reading main_file "', main_file, '"'
    df = pd.DataFrame.from_csv(main_file, index_col=False, sep='\t')
    array_main = df.as_matrix(columns=col)
    driver_trip = df.as_matrix(columns=['driver_trip'])

    X_train = array_main
    len_main = np.shape(array_main)[0]
    Y_train = np.ones(len_main)

    # for i in range(TRAIN_SIZE + 2):  # для нейросети
    for i in range(TRAIN_SIZE - 1):
        X_train = np.append(X_train, array_main, axis=0)
        Y_train = np.append(Y_train, np.ones(len_main))

    for train_file in train_files:
        # print 'Reading train_file "', train_file, '"'
        df = pd.DataFrame.from_csv(train_file, index_col=False, sep='\t')
        array_train = df.as_matrix(columns=col)
        len_train = np.shape(array_train)[0]
        X_train = np.append(X_train, array_train, axis=0)
        Y_train = np.append(Y_train, np.zeros(len_train))

    X_train = preprocessing.scale(X_train)
    X_train[np.isnan(X_train)] = 0.0
    X = X_train[0:len_main]

    return (X_train, Y_train, X, driver_trip)


def apply_svm(files, main_driver=1):
    """
    Applies SVM for identifying trips which are not from the driver of interest
    """

    (X_train, Y_train, X, driver_trip_arr) = get_train_data(files, main_driver)
    a = np.empty(shape=[0, 2])

    clf = svm.SVC(kernel='rbf', shrinking=True, verbose=False)
    clf.fit(X_train, Y_train)
    # print clf.get_params()
    print main_driver, ':',  clf.score(X_train, Y_train)

    i = 0
    for x in X:
        driver_trip = driver_trip_arr[i][0]
        prob = str(int(clf.predict(x)[0]))
        a = np.append(a, np.array([[driver_trip, prob]]), axis=0)
        i = i + 1

    print main_driver, ': ', sum([1 for p in a if p[1] == '1'])

    return a


def apply_dbn(files, main_driver=1):
    """
    Applies DBN for identifying trips which are not from the driver of interest
    """
    (X_train, Y_train, X, driver_trip_arr) = get_train_data(files, main_driver)
    a = np.empty(shape=[0, 2])

    net = DBN([len(col), 10, 2],
              learn_rates=0.3,
              learn_rate_decays=0.9,
              epochs=10,
              verbose=0)
    net.fit(X_train, Y_train)

    Y_dbn = net.predict(X_train)
    print main_driver, ':', 1 - zero_one_loss(Y_train, Y_dbn)
    # print "Classification report:"
    # print classification_report(Y_train, preds)

    i = 0
    Y = net.predict(X)
    for y in Y:
        driver_trip = driver_trip_arr[i][0]
        prob = str(int(Y[i]))
        a = np.append(a, np.array([[driver_trip, prob]]), axis=0)
        i = i + 1

    print main_driver, ': ', sum([1 for p in a if p[1] == '1'])

    return a


def apply_oneclasssvm(files, main_driver=1):
    """
    http://habrahabr.ru/post/251225/
    """
    main_file = [KPI_PATH + f for f in files
                 if int(os.path.splitext(f)[0]) == main_driver][0]
    df = pd.DataFrame.from_csv(main_file, index_col=False, sep='\t')

    driver_kpi = df.as_matrix(columns=col)
    driver_kpi = preprocessing.scale(driver_kpi)
    driver_kpi[np.isnan(driver_kpi)] = 0.0

    driver_trip_array = df.as_matrix(columns=['driver_trip'])

    pca = PCA(n_components=2)
    X = pca.fit_transform(driver_kpi)
    # print col
    # print pca.explained_variance_ratio_

    clf = svm.OneClassSVM(kernel="rbf")
    clf.fit(X)
    # print main_driver, 'predict:', sum([p for p in clf.predict(X) if p == 1])

    dist_to_border = clf.decision_function(X).ravel()

    # plt.hist(dist_to_border, bins=50)
    # plt.show()

    # a = np.array(dist_to_border)
    # a = np.sort(a[a < 0])
    # d = np.diff(a)
    # n = np.argmax(d)
    # while n < 5:
    #     d[n] = 0
    #     n = np.argmax(d)

    threshold = -10.0
    plot_oneclasssvm(main_driver, clf, X, dist_to_border, threshold)

    a = np.empty(shape=[0, 2])
    i = 0
    for x in X:
        driver_trip = driver_trip_array[i][0]
        prob = str(int(dist_to_border[i] > threshold and 1 or 0))
        a = np.append(a, np.array([[driver_trip, prob]]), axis=0)
        i = i + 1

    print main_driver, ': ', sum([1 for p in a if p[1] == '1'])

    return a


def plot_oneclasssvm(main_driver, clf, X, dist_to_border, threshold):
    """
    http://scikit-learn.org/stable/auto_examples/covariance/plot_outlier_detection.html
    """
    is_inlier = dist_to_border > threshold
    xx, yy = np.meshgrid(np.linspace(-7, 7, 500), np.linspace(-7, 7, 500))

    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    plt.title("Outlier detection")
    plt.contourf(xx, yy, Z,
                 levels=np.linspace(Z.min(), threshold, 7),
                 cmap=plt.cm.Blues_r)
    a = plt.contour(xx, yy, Z,
                    levels=[threshold],
                    linewidths=2,
                    colors='red')
    plt.contourf(xx, yy, Z, levels=[threshold, Z.max()], colors='orange')
    b = plt.scatter(X[is_inlier == 0, 0], X[is_inlier == 0, 1], c='red')
    c = plt.scatter(X[is_inlier == 1, 0], X[is_inlier == 1, 1], c='yellow')
    plt.axis('tight')
    plt.legend([a.collections[0], b, c],
               ['learned decision function', 'outliers', 'inliers'],
               prop=fm.FontProperties(size=11))
    plt.xlim((-7, 7))
    plt.ylim((-7, 7))
    plt.savefig(str(main_driver) + '_svm' + PLOT_EXT)
    plt.close()


# =============================================================================
# =============================================================================
# =============================================================================

############################################
tr = Trip.Trip(1, 29)
tr = Trip.Trip(1, 30)
tr = Trip.Trip(1, 31)
tr = Trip.Trip(1, 32)

############################################
# dr = Driver(driver_num=0, method='csv1')


############################################
# dirs = os.listdir(DRIVER_PATH)
# dirs = [x for x in dirs if not x.startswith('.')]
# dirs = map(int, dirs)
# dirs.sort()
# for i in dirs:
#     Driver(driver_num=i)

#############################################

# files = [f for f in os.listdir(KPI_PATH) if os.path.splitext(f)[1] == '.txt']
# submission = np.array([['driver_trip', 'prob']])
# driver_list = [int(os.path.splitext(f)[0]) for f in files]

# for n in sorted(driver_list):
#     # apply_oneclasssvm
#     # apply_svm
#     # apply_dbn
#     a = apply_dbn(files, n)
#     submission = np.append(submission, a, axis=0)

# np.savetxt('submission.csv', submission, fmt='%s', delimiter=',')

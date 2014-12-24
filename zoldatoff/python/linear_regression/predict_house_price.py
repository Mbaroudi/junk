#!/usr/bin/env python
#coding: utf-8

"""
Predicting cost price of  a house for ZooZoo
https://dataaspirant.wordpress.com/2014/12/20/linear-regression-implementation-in-python/
"""

import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
from sklearn import linear_model
#from sklearn.preprocessing import PolynomialFeatures
#from sklearn.pipeline import make_pipeline
#from sklearn.linear_model import Ridge


def get_data(file_name):
    """ Function to get data from csv file """

    data = pd.read_csv(file_name)
    x_parameter = []
    y_parameter = []
    for single_square_feet, single_price_value \
			in zip(data['square_feet'], data['price']):
        x_parameter.append([float(single_square_feet)])
        y_parameter.append(float(single_price_value))

    return x_parameter, y_parameter


def linear_model_main(x_parameters, y_parameters, predict_value):
    """ Function for Fitting our data to Linear model """

    # Create linear regression object
    regr = linear_model.LinearRegression()
    regr.fit(x_parameters, y_parameters)
    predict_outcome = regr.predict(predict_value)
    predictions = {}
    predictions['intercept'] = regr.intercept_
    predictions['coefficient'] = regr.coef_
    predictions['predicted_value'] = predict_outcome
    return predictions


def show_linear_line(x_parameters, y_parameters):
    """ Function to show the resutls of linear fit model """

    plt.scatter(x_parameters, y_parameters, color='blue')

    # Create linear regression object
    regr = linear_model.LinearRegression()
    regr.fit(x_parameters, y_parameters)
    plt.plot(x_parameters, regr.predict(x_parameters), color='red', linewidth=3)

    #regr2 = make_pipeline(PolynomialFeatures(degree=3), Ridge())
    #regr2.fit(x_parameters, y_parameters)
    #plt.plot(x_parameters, regr2.predict(x_parameters))

    plt.show()

X, Y = get_data('input_data.csv')

PREDICT_VALUE = 700
RESULT = linear_model_main(X, Y, PREDICT_VALUE)
print "Intercept value: ", RESULT['intercept']
print "coefficient: ", RESULT['coefficient']
print "Predicted value: ", RESULT['predicted_value']

show_linear_line(X, Y)

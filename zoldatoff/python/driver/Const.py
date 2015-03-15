#!/usr/bin/env python
# coding: utf-8

"""
Driver Telematics Analysis
==========================

Константы и параметры расчёта.
"""

DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
KPI_PATH = './kpi/'
PLOT_PATH = './plot/'

PLOT_EXT = '.png'

DEBUG = 0

COL = ['vR', 's', 'a', 'accel', 'decel', 'stop', 'calm', 'nerv_a', 'nerv_ang']

# Google Chart Color List
# http://there4development.com/blog/2012/05/02/google-chart-color-list/
COLORS = [
    '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#3B3EAC',
    '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395', '#994499',
    '#22AA99', '#AAAA11', '#6633CC', '#E67300', '#8B0707', '#329262',
    '#5574A6', '#3B3EAC'] * 20

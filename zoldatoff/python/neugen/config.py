#!/usr/bin/python

"""
Global parameters of the algorythm
"""

from math import pi

WIDTH = 1000			# main window width
HEIGHT = 700			# main window height

SPEED_OF_EATER = 200	# max speed of eaters
SPEED_OF_FOOD = 20		# max speed of food

CNT_EATERS = 15			# number of eaters
CNT_FOOD = 10			# number of food
CNT_ENV = 10				# number of environments

CNT_INPUT_FOOD = 5		# amount of seen food
CNT_INPUT_EATERS = 3	# count of seen eaters

EAT_DISTANCE = 10 		# on this distance the eater can eat the food
VISUAL_ANGLE = pi/2.0  	# the vision angle of the eater

TIME_TO_RESET = 10		# the period of time for an environment observation

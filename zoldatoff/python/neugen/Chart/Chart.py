#!/usr/bin/python

import pygal
from pygal.style import NeonStyle
from math import floor

# The number of points on plot will be reduced to 2*``npoints``
npoints = 15	


def movavg(x, y, dx):
	"""
	Function reduces the data length using moving average algorythm
	"""
	if dx <= 0:
		return (x, y)

	xx = list()
	yy = list()
	for i in range(len(x)/dx):
		s = sum(y[i*dx:i*dx+dx]) / dx
		xx.append(x[i*dx])
		yy.append(s)

	return (xx, yy)


def movmax(x, y, dx):
	"""
	Function reduces the data length using moving maximum algorythm
	"""
	if dx <= 0:
		return (x, y)

	xx = list()
	yy = list()
	for i in range(len(x)/dx):
		s = max(y[i*dx:i*dx+dx])
		xx.append(x[i*dx])
		yy.append(s)

	return (xx, yy)


class LineChart():
	"""
	Class LineChart contains of 3 2D plots
	"""
	def __init__(self, x, y1, y2, y3, fmov = movmax):
		
		chart = pygal.Line(
			#show_legend=False,
			#legend_at_bottom=True, 
			human_readable=True, 
			title='Evolution', 
			value_font_size=0, 
			label_font_size=15, 
			fill=True,
			interpolate='cubic', 
			style=NeonStyle)

		dx = floor(len(x) / npoints)
		dx = max(1, int(dx))

		(xx, yy) = fmov(x, y1, dx)
		
		# X-labels
		chart.x_labels = map(str, xx)

		# First plot
		chart.add('Best', yy)

		# Second plot
		(xx, yy) = fmov(x, y2, dx)
		chart.add('#1', yy)

		# Third plot
		(xx, yy) = fmov(x, y3, dx)
		chart.add('#2', yy)

		chart.render_to_file('chart.svg') 

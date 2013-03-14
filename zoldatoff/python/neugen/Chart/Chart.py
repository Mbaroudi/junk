#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygal
from pygal.style import NeonStyle
from math import floor

npoints = 15

# Скользящее среднее
def movavg(x, y, dx):
	if dx <= 0:
		return (x, y)

	xx = list()
	yy = list()
	for i in range(len(x)/dx):
		s = sum(y[i*dx:i*dx+dx]) / dx
		xx.append(x[i*dx])
		yy.append(s)

	return (xx, yy)


# Скользящее максимальное
def movmax(x, y, dx):
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
		
		chart.x_labels = map(str, xx)
		chart.add('Best', yy)

		(xx, yy) = fmov(x, y2, dx)
		chart.add('#1', yy)

		(xx, yy) = fmov(x, y3, dx)
		chart.add('#2', yy)

		chart.render_to_file('chart.svg') 

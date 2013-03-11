import pygal
from pygal.style import NeonStyle
from math import floor

class LineChart():
	def __init__(self, x, y):
		d = floor(len(x) / 20.0)
		d = max(1, int(d))
		xx = x[::d]
		yy = y[::d]

		chart = pygal.Line(
			show_legend=False, 
			human_readable=True, 
			title='Evolution', 
			value_font_size=0, 
			label_font_size=15, 
			fill=True,
			interpolate='cubic', 
			style=NeonStyle)
		chart.x_labels = map(str, xx)
		chart.add('Evolution', yy)
		chart.render_to_file('chart.svg') 

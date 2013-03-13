import pygal
from pygal.style import NeonStyle
from math import floor

class LineChart():
	def __init__(self, x, y1, y2, y3):
		
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

		d = floor(len(x) / 20.0)
		d = max(1, int(d))

		xx = x[::d]
		chart.x_labels = map(str, xx)

		yy = y1[::d]
		chart.add('Best', yy)

		yy = y2[::d]
		chart.add('#1', yy)

		yy = y3[::d]
		chart.add('#2', yy)

		chart.render_to_file('chart.svg') 

import pygal
from pygal.style import NeonStyle

class LineChart():
	def __init__(self, x, y):
		chart = pygal.Line(
			show_legend=False, 
			human_readable=True, 
			title='Evolution', 
			value_font_size=0, 
			label_font_size=15, 
			fill=True,
			interpolate='cubic', 
			style=NeonStyle)
		chart.x_labels = map(str, x)
		chart.add('Evolution', y)
		chart.render_to_file('chart.svg') 

#!/usr/bin/python

from Visual import Visual
from Neural import Neural
from Genetic import Genetic
import pyglet
import math
import random

width = 800
height = 600


# create the window, but keep it offscreen until we are done with setup
# http://www.pyglet.org/doc/api/pyglet.window.Window-class.html
window = pyglet.window.Window(width=800, height=600, style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS, visible=False, caption="Neutral network evolution")

# centre the window on whichever screen it is currently on (in case of multiple monitors)
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)


# create a batch to perform all our rendering
batch = pyglet.graphics.Batch()


pacmans = list()
hamburgers = list()
for i in range(10):
	pacmans.append( Visual.Actor(window, batch, 100*random.random(), 'pacman.png') )
	hamburgers.append( Visual.Actor(window, batch, 10*random.random(), 'burger.png') )

neurals = list()
for i in range(10):
	neurals.append( Neural.MLP(10, 10, 1) )


def dist(x, y):
	return math.sqrt(x*x+y*y)

def run_neural():
	max_distance = dist(width, height)
	max_angle = 2 * math.pi
	eaten_food = 0

	for i in range(10):
		input = list()
		for j in range(10):
			if hamburgers[j] == None:
				angle = 0
				distance = 0
			else:	
				distance = dist(pacmans[i].x - hamburgers[j].x, pacmans[i].y - hamburgers[j].y)
				angle = math.acos( (hamburgers[j].x - pacmans[i].x) / distance )

				if distance <= 10:
					#angle = 0
					#del hamburgers[j]
					hamburgers[j] = None
					pacmans[i].add_food()
				#else: angle = math.acos( (hamburgers[j].x - pacmans[i].x) / distance )

			input += [distance / max_distance, angle / max_angle]
		
		neural = neurals[i]
		output = neural.run(input)
		pacmans[i].set_radian(2 * math.pi * output[0])
		eaten_food += pacmans[i].food

	if eaten_food >= 2:
		next_evolution()
		for i in range(10):
			if hamburgers[i] == None:
				hamburgers[i] = Visual.Actor(window, batch, 10*random.random(), 'burger.png')


def next_evolution():
	persons = list()
	results = list()
	for i in range(len(neurals)):
		persons.append(neurals[i].export2vector())
		results.append(pacmans[i].food)
		pacmans[i].food = 0

	population = Genetic.Population(persons, results)
	superpersons = population.evolution()

	for superperson in superpersons:
		neurals[i].import_vector(superperson)

	print 'evolution completed!'

# clear the window and draw the scene
@window.event
def on_draw():
	window.clear()
	batch.draw()

def update(dt):
	run_neural()
	[pacmans[i].update(dt) for i in range(10)]
	for i in range(10):
		if hamburgers[i]: 
			hamburgers[i].update(dt)


# schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)

# clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()				# Clear the window
window.flip()				# Swap the OpenGL front and back buffers.
window.set_visible(True)	# make the window visible at last

# finally, run the application
pyglet.app.run()
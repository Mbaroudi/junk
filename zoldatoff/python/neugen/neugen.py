#!/usr/bin/python

from Visual import Visual
from Neural import Neural
from Genetic import Genetic
import pyglet
import math
import random

width = 800
height = 600

pacman_velocity = 200
hamburger_velocity = 0


# create the window, but keep it offscreen until we are done with setup
# http://www.pyglet.org/doc/api/pyglet.window.Window-class.html
window = pyglet.window.Window(width=800, height=600, style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS, visible=False, caption="Neutral network evolution")

# centre the window on whichever screen it is currently on (in case of multiple monitors)
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)

# setup a key handler to track keyboard input
keymap = pyglet.window.key.KeyStateHandler()
window.push_handlers(keymap)

# create a batch to perform all our rendering
batch = pyglet.graphics.Batch()


evolution_label = pyglet.text.Label('Evolution = 0', font_name='Arial', font_size=24, x=10, y=60, anchor_x='left', anchor_y='center', batch=batch)
food_label = pyglet.text.Label('Food = 0', font_name='Arial', font_size=24, x=10, y=30, anchor_x='left', anchor_y='center', batch=batch)

pacmans = list()
hamburgers = list()
for i in range(10):
	pacmans.append( Visual.Actor(window, batch, pacman_velocity*random.random(), 'pacman.png') )
	hamburgers.append( Visual.Actor(window, batch, hamburger_velocity*random.random(), 'burger.png') )

neurals = list()
for i in range(10):
	neurals.append( Neural.MLP(10, 20, 1) )

evolution_num = 0
time = 0

def dist(x, y):
	return math.sqrt(x*x+y*y)

def run_neural():
	global time
	max_distance = dist(width, height)
	max_angle = 2 * math.pi
	eaten_food = 0
	food_label.text = 'Food = ' + str(eaten_food)

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
		food_label.text = 'Food = ' + str(eaten_food)

	if eaten_food >= 2:
		next_evolution()
		time = 0
		for i in range(10):
			if hamburgers[i] == None:
				hamburgers[i] = Visual.Actor(window, batch, hamburger_velocity*random.random(), 'burger.png')
			pacmans[i].reset()
			hamburgers[i].reset()


def next_evolution():
	global evolution_num
	global pacmans
	global hamburgers
	global neurals

	persons = list()
	results = list()
	for i in range(len(neurals)):
		person = neurals[i].export2vector()
		persons.append(person)
		results.append(pacmans[i].food)
		pacmans[i].food = 0

	population = Genetic.Population(persons, results)
	superpersons = population.evolution()

	for superperson in superpersons:
		neurals[i].import_vector(superperson)

	evolution_num += 1	
	evolution_label.text = 'Evolution = ' + str(evolution_num)
	print 'evolution #' ,evolution_num, 'completed!'

# clear the window and draw the scene
@window.event
def on_draw():
	window.clear()
	batch.draw()

def update(dt):
	global time
	time += dt

	run_neural()

	[pacmans[i].update(dt) for i in range(10)]

	for i in range(10):
		if hamburgers[i]: 
			hamburgers[i].update(dt)

	if keymap[pyglet.window.key.SPACE] or time > 20:
		time = 0
		[pacmans[i].reset() for i in range(10)]
		for i in range(10):
			if hamburgers[i]: 
				hamburgers[i].reset()


# schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)

# clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()				# Clear the window
window.flip()				# Swap the OpenGL front and back buffers.
window.set_visible(True)	# make the window visible at last

# finally, run the application
pyglet.app.run()
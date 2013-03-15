#!/usr/bin/python

"""
Neural network evolution using genetic algorythm

This program uses genetic algorythm to teach the eaters to eat food.

The eaters are driven by a neural network. To understand the efficiency of such a network 
we create an environment of actors (eaters and food) and observe it for a period of time. 
Then we look at the amount of eaten food (and several least significant parameters) to 
range the network relative to other neural networks (in other environments)

We create several environments with several different (random) networks and observe them.
Then we combine the neural networks and generate new ones using genetic algorythm. And the story
continues.

"""

from config  import *			# Global CONSTANTS
from Visual  import Visual 		# Actors visualisation
from Neural  import Neural 		# Neural netvork
from Genetic import Genetic 	# Genetic algorythm
from Chart   import Chart 		# Generate 2D plot

from math import sqrt, acos, pi
from random import random

import pyglet					# OpenGL library

##############################################################

def dist(x, y):
	""" Length of a vecror """
	return sqrt(x*x + y*y)


def create_food(window, batch):
	""" Create actor (food) in a random position """
	return Visual.Food(window, batch, SPEED_OF_FOOD*random())


def create_eater(window, batch):
	""" Create actor (eater) in a random position """
	return Visual.Eater(window, batch, SPEED_OF_EATER*random())


def create_neural():
	""" 
	Create a random neural network with ``cnt_input`` inputs and ``2`` outputs
	Input: 
	 * food distance and angle (``CNT_INPUT_FOOD``)
	 * eaters distance and angle (``CNT_INPUT_EATERS``)
	Output:
	 * angle to rotate
	 * velocity increment
	"""
	
	cnt_input  = 2*CNT_INPUT_FOOD + 2*CNT_INPUT_EATERS
	cnt_hidden = cnt_input
	cnt_output = 2

	return Neural.MLP(cnt_input, cnt_hidden, cnt_output)


def relative_position(actor1, actor2):
	"""
	Function calculates the direction to the ``actor2`` relative to ``actor1``
	Returns normalized values:
	 * angle to rotate towards ``actor2`` (angle / 2*pi afer normalization)
	 * distance between ``actor1`` and ``actor2`` (after normalization: ``EAT_DISTANCE`` / distance)
	 * if ``actor2`` is close to ``actor1`` (distance < ``EAT_DISTANCE``) then ``actor2`` can be eaten

	``actor1`` can see only straight in front of him. Visual angle = ``VISUAL_ANGLE``	
	"""

	inf_distance = 100000.0		# infinity
	eaten = False

	# Actor2 was already eaten
	if actor2 == None:
		return {'delta_angle': 0.0, 'distance': EAT_DISTANCE / inf_distance, 'eaten': eaten}

	# Distance between actors	
	distance = dist(actor2.x - actor1.x, actor2.y - actor1.y)
	distance = max(distance, 1)

	# Direction to actor2
	angle = acos( (actor2.x - actor1.x) / distance )

	# Relative direction from actor1 to actor2
	if actor2.y > actor1.y:
		delta_angle = (angle - actor1.angle) % (2*pi)
	else:
		delta_angle = (- angle - actor1.angle) % (2*pi)

	if delta_angle > pi:
		delta_angle = delta_angle - 2*pi

	# Check: can we see actor2?
	if -VISUAL_ANGLE/2 < delta_angle < VISUAL_ANGLE/2:
		distance = inf_distance		

	# Check: can we eat actor2?
	if distance < EAT_DISTANCE:
		eaten = True

	# Normalize values before return
	return {'delta_angle': delta_angle / (2.0*pi), 'distance': EAT_DISTANCE / distance, 'eaten': eaten}


def draw_chart(x, yy):
	"""
	Create an svg file with 3 plots:
	 * best environment result
	 * first (previous best) environment result
	 * second (previous best) environment result

	One point on each plot after every revolution
	"""

	global chart_x
	global chart1_y
	global chart2_y
	global chart3_y

	chart_x.append( x )
	chart1_y.append( max(yy) )
	chart2_y.append( yy[0] )
	chart3_y.append( yy[1] )

	chart = Chart.LineChart(chart_x, chart1_y, chart2_y, chart3_y)


def revolution():
	"""
	Renew the neural networks in all environments:
	 * Combine neural networks from all environments
	 * Define the value of fitness funtion for every network
	 * Run genetic algorithm and produce new neural networks
	"""
	global evolution_num
	global evolution_label
	global evolution_sound
	global env

	# Neural networks ant their efficiency
	neurals = [ env[i].export2vector() for i in range(CNT_ENV) ]
	results = [ env[i].get_result()    for i in range(CNT_ENV) ]
	
	# Run genetic algorythm on neural networks
	population = Genetic.Population(neurals, results)
	neurals = population.evolution(3)

	# The result is imported into existing environments
	for i in range(CNT_ENV):
		env[i].import_vector(neurals[i])

	# Bring info to user: plot, label, sound
	draw_chart(evolution_num, results)	
	evolution_num += 1
	evolution_label.text = 'Evolution = ' + str(evolution_num)
	evolution_sound.play()


def update(dt):
	"""
	Updates the screen:
	 * moves all the actors of ``current_env`` envoronment
	 * wakes up the next evironment every ``TIME_TO_RESET`` seconds
	 * wakes up the next evironment after SPACE key is pressed
	 * updates text labels on the screen
	 * revolution occurs after the last (``CNT_ENV``) environment fell asleep
	"""
	global time
	global env
	global current_env

	time += dt

	env[current_env].movement(dt)

	if keymap[pyglet.window.key.SPACE] or time > TIME_TO_RESET:
		env[current_env].sleep()

		if current_env + 1 < CNT_ENV:
			current_env += 1
		else:
			current_env = 0
			revolution()

		env[current_env].wake()
		time = 0

	current_result = env[current_env].get_result()
	fitness_label.text = 'Fitness = ' + str(round(current_result, 3))	
	env_label.text = 'Environment = ' + str(current_env)

############################################################

class Environ():
	"""
	Environment class

	Environment consists of:
	 * actors: eaters and food
	 * neural network = brain of all eaters
	"""

	def __init__(self, window, batch, neural):
		self.window = window
		self.batch = batch
		self.neural = neural

		self.sleep()

	def sleep(self):
		""" Removes actors from the screen """
		self.eaters = list()
		self.food = list()

	def wake(self):
		""" Creates actors on the screen """
		self.result = 0
		self.eaters = [ create_eater(self.window, self.batch) for i in range(CNT_EATERS) ]
		self.food 	= [ create_food(self.window, self.batch)  for i in range(CNT_FOOD) ]

	def export2vector(self):
		return self.neural.export2vector()

	def import_vector(self, vector):
		self.neural.import_vector(vector)

	def get_result(self):
		""" Sum of fitness functions of all the eaters """
		return self.result

	def movement(self, dt):
		""" Checks the position of actors and makes a movement """

		for i in range(CNT_EATERS):

			# Make a list of all surrounding food
			input_food = list()			
			for j in range(CNT_FOOD):
				position = relative_position(self.eaters[i], self.food[j])
				input_food.append(position) 

				# Recreate eaten food
				if position['eaten']:	
					self.eaters[i].inc_food()
					self.food[j] = create_food(self.window, self.batch)
				
		
			# Make a list of all surrounding eaters
			input_eaters = list()		
			for j in range(CNT_EATERS):
				if i != j:
					position = relative_position(self.eaters[i], self.eaters[j])
					input_eaters.append(position)
			
			# Bring the nearest actors to the start of the list
			input_food.sort(key=lambda x:x['distance'], reverse=True)
			input_eaters.sort(key=lambda x:x['distance'], reverse=True)

			# Make a list of CNT_INPUT_FOOD nearest food and CNT_INPUT_EATERS nearest eaters
			input = list()

			for j in range(CNT_INPUT_FOOD):
				input.append(input_food[j]['distance'])
				input.append(input_food[j]['delta_angle'])

			for j in range(CNT_INPUT_EATERS):
				input.append(input_eaters[j]['distance'])
				input.append(input_eaters[j]['delta_angle'])				

			# Use the universal brains od an eater
			output = self.neural.run(input)

			# Result of thinking: rotate and change velocity
			self.eaters[i].inc_angle( pi * output[0] )
			self.eaters[i].inc_speed( SPEED_OF_EATER/100.0*output[1] )

		# Make a movement for every actor
		for i in range(CNT_EATERS):
			self.eaters[i].movement(dt)

		for i in range(CNT_FOOD):
			if self.food[i]: 
				self.food[i].movement(dt)

		# Renew the environment result (sum of all fitness functions of the eaters)
		self.result = sum([self.eaters[i].fitness() for i in range(CNT_EATERS)])

############################################################

# Create the window, but keep it offscreen until we are done with setup
# http://www.pyglet.org/doc/api/pyglet.window.Window-class.html
window = pyglet.window.Window(
	width=WIDTH, 
	height=HEIGHT, 
	style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS, 
	visible=False, 
	caption="Neutral network evolution")

# Clear the window and draw the scene
@window.event
def on_draw():
	window.clear()
	batch.draw()

# Centre the window on whichever screen it is currently on (in case of multiple monitors)
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)

# Setup a key handler to track keyboard input
keymap = pyglet.window.key.KeyStateHandler()
window.push_handlers(keymap)

# Create a batch to perform all our rendering
batch = pyglet.graphics.Batch()


# Create text labels with information about the state 
evolution_label = pyglet.text.Label(
	'Evolution = 0', 
	font_name='Arial', 
	font_size=12, 
	x=10, y=60, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

env_label = pyglet.text.Label(
	'Environment = 0', 
	font_name='Arial', 
	font_size=12, 
	x=10, y=40, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

fitness_label = pyglet.text.Label(
	'Fitness = 0', 
	font_name='Arial', 
	font_size=12, 
	x=10, y=20, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

# Sound of the next evolution
evolution_sound = pyglet.resource.media('genetic.mp3', streaming=False)

# Schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)

# Clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()				# Clear the window
window.flip()				# Swap the OpenGL front and back buffers.
window.set_visible(True)	# Make the window visible at last


#################

# Current environment number
current_env = 0	

# How many times the revolution occured
evolution_num = 0

# Duration of the environment wake
time = 0.0

# Charts' data
chart_x  = list()
chart1_y = list()
chart2_y = list()
chart3_y = list()

# Initialize the environments (CNT_ENV)
env = [ Environ(window, batch, create_neural()) for i in range(CNT_ENV) ]
env[current_env].wake()

#################

# Finally, run the application
pyglet.app.run()
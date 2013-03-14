#!/usr/bin/python
# -*- coding: utf-8 -*-

from Visual import Visual
from Neural import Neural
from Genetic import Genetic
from Chart import Chart
import pyglet
import math
from random import random, uniform
from time import time as systime

from config import *

##############################################################

def dist(x, y):
	return math.sqrt(x*x+y*y)

def create_food(window, batch):
	return Visual.Food(window, batch, SPEED_OF_FOOD*random())

def create_eater(window, batch):
	return Visual.Eater(window, batch, SPEED_OF_EATER*random())

def create_neural():
	# на вход сети подаем расстояние до пищи и пожирателей и направление на них
	# на выходе получаем угол поворота и прирост скорости
	
	cnt_input = 2*CNT_INPUT_FOOD + 2*CNT_INPUT_EATERS
	cnt_hidden = cnt_input
	cnt_output = 2

	return Neural.MLP(cnt_input, cnt_hidden, cnt_output)


def relative_position(actor1, actor2):
	inf_distance = 100000.0
	eaten = False

	if actor2 == None:
		return {'delta_angle': 0.0, 'distance': EAT_DISTANCE / inf_distance, 'eaten': eaten}

	distance = dist(actor2.x - actor1.x, actor2.y - actor1.y)
	distance = max(distance, 1)

	# направление к еде
	angle = math.acos( (actor2.x - actor1.x) / distance )

	# поворот к еде
	if actor2.y > actor1.y:
		delta_angle = (angle - actor1.angle) % (2*math.pi)
	else:
		delta_angle = (- angle - actor1.angle) % (2*math.pi)

	if delta_angle > math.pi:
		delta_angle = delta_angle - 2*math.pi

	# видим ли мы под этим углом	
	if -VISUAL_ANGLE/2 < delta_angle < VISUAL_ANGLE/2:
		distance = inf_distance		

	if distance < EAT_DISTANCE:
		eaten = True

	return {'delta_angle': delta_angle / (2.0*math.pi), 'distance': EAT_DISTANCE / distance, 'eaten': eaten}


def draw_chart(x, yy):
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
	global evolution_num
	global evolution_label
	global evolution_sound
	global env

	# Параметры эволюционного алогоритма: особи и их ранги
	neurals = [ env[i].export2vector() for i in range(CNT_ENV) ]
	results = [ env[i].get_result()    for i in range(CNT_ENV) ]
	
	# Создание популляции и нового поколения	
	population = Genetic.Population(neurals, results)
	neurals = population.evolution(3)
	for i in range(CNT_ENV):
		env[i].import_vector(neurals[i])

	# рекация на создание нового поколения	
	draw_chart(evolution_num, results)

	evolution_num += 1	
	evolution_label.text = 'Evolution = ' + str(evolution_num)
	evolution_sound.play()


def update(dt):
	global time
	global env
	global current_env

	time += dt

	env[current_env].movement(dt)

	fitness_label.text = 'Fitness = ' + str(env[current_env].get_result())	

	if keymap[pyglet.window.key.SPACE] or time > TIME_TO_RESET:
		env[current_env].sleep()

		if current_env + 1 < CNT_ENV:
			current_env += 1
		else:
			current_env = 0
			revolution()

		env[current_env].wake()
		time = 0

############################################################

class Environ():
	def __init__(self, window, batch, neural):
		self.window = window
		self.batch = batch
		self.neural = neural

		self.sleep()

	def wake(self):
		self.reborn()

	def sleep(self):
		self.eaters = list()
		self.food = list()

	def reborn(self):
		self.result = 0
		self.eaters = [ create_eater(self.window, self.batch) for i in range(CNT_EATERS) ]
		self.food 	= [ create_food(self.window, self.batch)  for i in range(CNT_FOOD) ]

	def export2vector(self):
		return self.neural.export2vector()

	def import_vector(self, vector):
		self.neural.import_vector(vector)

	def get_result(self):
		return self.result

	def movement(self, dt):
		for i in range(CNT_EATERS):
			# Для каждого пожирателя перебираем всю еду 
			# подготавливаем входной вектор (input) для нейронной сети

			input_food = list()
			for j in range(CNT_FOOD):
				position = relative_position(self.eaters[i], self.food[j])

				if position['eaten']:
					self.food[j] = create_food(self.window, self.batch)
					self.eaters[i].inc_food()

				input_food.append(position) 
		
			input_eaters = list()	
			for j in range(CNT_EATERS):
				if i != j:
					position = relative_position(self.eaters[i], self.eaters[j])
					input_eaters.append(position)
			
			input_food.sort(key=lambda x:x['distance'], reverse=True)
			input_eaters.sort(key=lambda x:x['distance'], reverse=True)

			input = list()

			for j in range(CNT_INPUT_FOOD):
				input.append(input_food[j]['distance'])
				input.append(input_food[j]['delta_angle'])

			for j in range(CNT_INPUT_EATERS):
				input.append(input_eaters[j]['distance'])
				input.append(input_eaters[j]['delta_angle'])				

			# Запускаем нейронную сеть пожирателя
			output = self.neural.run(input)

			# Меняем направление и скорость движения пожирателя
			self.eaters[i].inc_angle( math.pi * output[0] )
			self.eaters[i].inc_speed( SPEED_OF_EATER/100.0*output[1] )

		for i in range(CNT_EATERS):
			self.eaters[i].movement(dt)

		for i in range(CNT_FOOD):
			if self.food[i]: 
				self.food[i].movement(dt)

		self.result = sum([self.eaters[i].fitness() for i in range(CNT_EATERS)])

############################################################

# create the window, but keep it offscreen until we are done with setup
# http://www.pyglet.org/doc/api/pyglet.window.Window-class.html
window = pyglet.window.Window(
	width=WIDTH, 
	height=HEIGHT, 
	style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS, 
	visible=False, 
	caption="Neutral network evolution")

# clear the window and draw the scene
@window.event
def on_draw():
	window.clear()
	batch.draw()

# centre the window on whichever screen it is currently on (in case of multiple monitors)
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)

# setup a key handler to track keyboard input
keymap = pyglet.window.key.KeyStateHandler()
window.push_handlers(keymap)

# create a batch to perform all our rendering
batch = pyglet.graphics.Batch()


# Crete text labels with information about the state 
evolution_label = pyglet.text.Label(
	'Evolution = 0', 
	font_name='Arial', 
	font_size=24, 
	x=10, y=60, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

fitness_label = pyglet.text.Label(
	'Fitness = 0', 
	font_name='Arial', 
	font_size=24, 
	x=10, y=30, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

evolution_sound = pyglet.resource.media('genetic.mp3', streaming=False)

# schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)

# clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()				# Clear the window
window.flip()				# Swap the OpenGL front and back buffers.
window.set_visible(True)	# make the window visible at last



#################

current_env = 0

# Количество "прогонов" генетического алгоритма
evolution_num = 0
chart_x  = list()
chart1_y = list()
chart2_y = list()
chart3_y = list()

# Время, прошедшее с последней перестановки "игроков"
time = 0.0

# Initialize the actors: eaters will eat the food.
# Neural networks will control the eaters
env = [ Environ(window, batch, create_neural()) for i in range(CNT_ENV) ]
env[current_env].wake()


# finally, run the application
pyglet.app.run()
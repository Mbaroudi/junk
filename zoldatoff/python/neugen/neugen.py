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

def fitness(food, distance, spin):
	#print  food, 2*distance / 100000,  2*spin / 10000
	return food - 2*distance / 100000 - 2*spin / 10000

def create_food():
	global window
	global batch
	return Visual.Actor(window, batch, SPEED_OF_FOOD*random(), 'food.png')

def create_eater():
	global window
	global batch
	eater = Visual.Actor(window, batch, SPEED_OF_EATER*random(), 'pacman.png')
	return eater

def create_neural():
	# на вход сети подаем расстояние до пищи и пожирателей и направление на них
	# на выходе получаем угол поворота и прирост скорости
	
	#cnt_input = 2*CNT_FOOD + 2*CNT_EATERS - 2
	cnt_input = 2*CNT_INPUT_FOOD + 2*CNT_INPUT_EATERS
	cnt_hidden = cnt_input
	cnt_output = 2

	return Neural.MLP(cnt_input, cnt_hidden, cnt_output)


def reset_actors():
	global eaters
	global food
	global time

	time = 0.0

	for i in range(CNT_FOOD):
		if food[i] == None:
			# Восстанавливаем съеденный гамбургер
			food[i] = create_food()
		else:
			food[i].reset(SPEED_OF_FOOD*random())
	
	for i in range(CNT_EATERS):
		eaters[i].reset(SPEED_OF_EATER*random())

def normalize_position(actor1, actor2):
	inf_distance = 100000.0
	eaten = False

	if actor2 == None:
		return {'delta_angle': 0.0, 'distance': EAT_DISTANCE / inf_distance, 'eaten': eaten}

	distance = dist(actor2.x - actor1.x, actor2.y - actor1.y)
	distance = max(distance, 1)

	# направление к еде
	angle = math.acos( (actor2.x - actor1.x) / distance )

	# поворок к еде
	if actor2.y > actor1.y:
		delta_angle = (angle - actor1.angle) % (2*math.pi)
	else:
		delta_angle = (- angle - actor1.angle) % (2*math.pi)

	if delta_angle > math.pi:
		delta_angle = delta_angle - 2*math.pi

	# видим ли мы под этим углом	
	if -VISUAL_ANGLE/2 < delta_angle < VISUAL_ANGLE/2:
		distance = inf_distance		
		#distance = None
		#delta_angle = 0

	#if distance > dist(WIDTH, HEIGHT) / 2:
	#	distance = inf_distance

	if distance < EAT_DISTANCE:
		eaten = True

	return {'delta_angle': delta_angle / (2.0*math.pi), 'distance': EAT_DISTANCE / distance, 'eaten': eaten}

def run_neural():
	global time
	global food_label
	global food
	global eaters
	global neurals

	# Локальная переменна для подсчета всей съеденной еды
	eaten_food = 0

	for i in range(CNT_EATERS):
		# Для каждого пожирателя перебираем всю еду 
		# подготавливаем входной вектор (input) для нейронной сети
		input = list()

		input_food = list()
		for j in range(CNT_FOOD):
			position = normalize_position(eaters[i], food[j])

			if position['eaten']:
				food[j] = create_food()
				eaters[i].inc_food()

			input_food.append(position) 
			#input += [ position['distance'], position['delta_angle'] ]
	
		input_eaters = list()	
		for j in range(CNT_EATERS):
			if i != j:
				position = normalize_position(eaters[i], eaters[j])
				input_eaters.append(position)
				#input += [ position['distance'], position['delta_angle'] ]
		
		input_food.sort(key=lambda x:x['distance'], reverse=True)
		input_eaters.sort(key=lambda x:x['distance'], reverse=True)

		for j in range(CNT_INPUT_FOOD):
			input.append(input_food[j]['distance'])
			input.append(input_food[j]['delta_angle'])

		for j in range(CNT_INPUT_EATERS):
			input.append(input_eaters[j]['distance'])
			input.append(input_eaters[j]['delta_angle'])				

		# Запускаем нейронную сеть пожирателя
		neural = neurals[i]
		output = neural.run(input)

		# Меняем направление и скорость движения пожирателя
		eaters[i].inc_angle_speed(math.pi * output[0], SPEED_OF_EATER/100.0*output[1])

		# Сохраняем информацию о съеденной еде
		eaten_food += eaters[i].food

	# Выводим инфмормацию о съеденной еде
	food_label.text = 'Food = ' + str(eaten_food)	

	# Запускаем генетический алгоритм
	if eaten_food >= MAX_FOOD:
		next_evolution()


def next_evolution():
	global evolution_num
	global evolution_label
	global eaters
	global food
	global neurals
	global start_time

	# Параметры эволюционного алогоритма: особи и их ранги
	persons = list()
	results = list()
	for i in range(CNT_EATERS):
		person = neurals[i].export2vector()
		persons.append(person)

		result = fitness(eaters[i].food, eaters[i].distance, eaters[i].spin)
		results.append(eaters[i].food)
		
		eaters[i].food = 0
		eaters[i].spin = 0
		eaters[i].distance = 0

	# Создание популляции и нового поколения	
	population = Genetic.Population(persons, results)
	superpersons = population.evolution()
	for i in range(CNT_EATERS):
		neurals[i].import_vector(superpersons[i])

	# рекация на создание нового поколения	
	evolution_num += 1	
	evolution_label.text = 'Evolution = ' + str(evolution_num)
	evolution_sound.play()
	
	current_time = systime()
	chart_x.append(evolution_num)
	chart_y.append(current_time - start_time)
	chart = Chart.LineChart(chart_x, chart_y)
	start_time = current_time

	reset_actors()


def update(dt):
	global time
	global eaters
	global food

	time += dt

	run_neural()

	for i in range(CNT_EATERS):
		eaters[i].update(dt)

	for i in range(CNT_FOOD):
		if food[i]: 
			food[i].update(dt)

	if keymap[pyglet.window.key.SPACE] or time > TIME_TO_RESET:
		reset_actors()


############################################################

# Количество "прогонов" генетического алгоритма
evolution_num = 0
chart_x = list()
chart_y = list()

start_time = systime()

# Время, прошедшее с последней перестановки "игроков"
time = 0.0

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

evolution_sound = pyglet.resource.media('genetic.mp3', streaming=False)

# Crete text labels with information about the state 
evolution_label = pyglet.text.Label(
	'Evolution = 0', 
	font_name='Arial', 
	font_size=24, 
	x=10, y=60, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

food_label = pyglet.text.Label(
	'Food = 0', 
	font_name='Arial', 
	font_size=24, 
	x=10, y=30, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

# Initialize the actors: eaters will eat the food.
# Neural networks will control the eaters
eaters = list()
for i in range(CNT_EATERS):
	eaters.append( create_eater() )

food = list()
for i in range(CNT_FOOD):	
	food.append( create_food() )

neurals = list()
for i in range(CNT_EATERS):
	neurals.append( create_neural() )


# schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)

# clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()				# Clear the window
window.flip()				# Swap the OpenGL front and back buffers.
window.set_visible(True)	# make the window visible at last

# finally, run the application
pyglet.app.run()

##########################################
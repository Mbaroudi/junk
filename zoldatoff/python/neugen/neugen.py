#!/usr/bin/python
# -*- coding: utf-8 -*-

from Visual import Visual
from Neural import Neural
from Genetic import Genetic
import pyglet
import math
from random import random, uniform

##############################################################

width = 800				# main window width
height = 600			# main window height

pacman_velocity = 400	# max velocity of eaters
hamburger_velocity = 0	# max velocity of food

cnt_pacman = 10			# number of eaters
cnt_hamburgers = 10		# number of food
cnt_hidden = 20 		# number of neurons in hidden layer

eat_distance = 10.0		# расстояние, на котором пожиратель может съесть еду

max_food = 8 			# на каком количестве съеденной пищи запускается генетический алгоритм

time_to_reset = 5.0		# через сколько секунд обновить положение игроков на экране


##############################################################

##########################################

def dist(x, y):
	return math.sqrt(x*x+y*y)

def reset_actors():
	global pacmans
	global hamburgers
	global time

	time = 0

	for i in range(cnt_hamburgers):
		if hamburgers[i] != None:
			hamburgers[i].reset()
	
	for i in range(cnt_pacman):
		pacmans[i].reset()

def reset_food():
	for i in range(cnt_hamburgers):
		if hamburgers[i] == None:
			hamburgers[i] = Visual.Actor(window, batch, hamburger_velocity*random(), 'burger.png')

def run_neural():
	global time
	global food_label
	global eat_distance
	global max_food

	# Локальная переменна для подсчета всей съеденной еды
	eaten_food = 0

	for i in range(cnt_pacman):
		# Для каждого пожирателя перебираем всю еду 
		# подготавливаем входной вектор (input) для нейронной сети
		input = list()

		for j in range(cnt_hamburgers):
			if hamburgers[j] == None:	# еда уже съедена
				angle = 0.0
				distance = 100000.0
			else:	
				distance = dist(pacmans[i].x - hamburgers[j].x, pacmans[i].y - hamburgers[j].y)

				if hamburgers[j].y > pacmans[i].y:
					angle = math.acos( (hamburgers[j].x - pacmans[i].x) / distance ) - pacmans[i].angle
				else:
					angle = - math.acos( (hamburgers[j].x - pacmans[i].x) / distance ) - pacmans[i].angle

				if distance <= eat_distance:		# съедаем еду
					#hamburgers[j] = None # еда исчезает
					hamburgers[j] = Visual.Actor(window, batch, hamburger_velocity*random(), 'burger.png')
					pacmans[i].add_food()

			input += [ eat_distance / distance, angle / (2.0*math.pi)]
		
		# Запускаем нейронную сеть пожирателя
		neural = neurals[i]
		output = neural.run(input)

		# Меняем направление движения пожирателя
		pacmans[i].set_radian(2.0 * math.pi * output[0])

		# Сохраняем информацию о съеденной еде
		eaten_food += pacmans[i].food

	# Выводим инфмормацию о съеденной еде
	food_label.text = 'Food = ' + str(eaten_food)	

	# Запускаем генетический алгоритм
	if eaten_food >= max_food:
		next_evolution()


def next_evolution():
	global evolution_num
	global evolution_label
	global pacmans
	global hamburgers
	global neurals
	global cnt_pacman

	persons = list()
	results = list()
	for i in range(cnt_pacman):
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

	reset_food()
	reset_actors()


def update(dt):
	global time
	global pacmans
	global hamburgers
	global cnt_pacman
	global cnt_hamburgers

	time += dt

	run_neural()

	for i in range(cnt_pacman):
		pacmans[i].update(dt)

	for i in range(cnt_hamburgers):
		if hamburgers[i]: 
			hamburgers[i].update(dt)

	if keymap[pyglet.window.key.SPACE] or time > time_to_reset:
		reset_actors()


############################################################

# Количество "прогонов" генетического алгоритма
evolution_num = 0

# Время, прошедшее с последней перестановки "игроков"
time = 0.0

# create the window, but keep it offscreen until we are done with setup
# http://www.pyglet.org/doc/api/pyglet.window.Window-class.html
window = pyglet.window.Window(
	width=width, 
	height=height, 
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

food_label = pyglet.text.Label(
	'Food = 0', 
	font_name='Arial', 
	font_size=24, 
	x=10, y=30, 
	anchor_x='left', anchor_y='center', 
	batch=batch)

# Initialize the actors: eaters will eat the food.
# Neural networks will control the eaters
pacmans = list()
for i in range(cnt_pacman):
	pacmans.append( Visual.Actor(window, batch, pacman_velocity*uniform(0.5, 1.0), 'pacman.png') )

hamburgers = list()
for i in range(cnt_hamburgers):	
	hamburgers.append( Visual.Actor(window, batch, hamburger_velocity*random(), 'burger.png') )

neurals = list()
for i in range(cnt_pacman):
	neurals.append( Neural.MLP(cnt_hamburgers, cnt_hidden, 1) )


# schedule the update function, 60 times per second
pyglet.clock.schedule_interval(update, 1.0/60.0)

# clear and flip the window, otherwise we see junk in the buffer before the first frame
window.clear()				# Clear the window
window.flip()				# Swap the OpenGL front and back buffers.
window.set_visible(True)	# make the window visible at last

# finally, run the application
pyglet.app.run()

##########################################
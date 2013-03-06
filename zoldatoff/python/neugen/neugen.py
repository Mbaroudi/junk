#!/usr/bin/python
# -*- coding: utf-8 -*-

from Visual import Visual
from Neural import Neural
from Genetic import Genetic
import pyglet
import math
from random import random, uniform

from config import *

##############################################################

def dist(x, y):
	return math.sqrt(x*x+y*y)

def create_food():
	global window
	global batch
	return Visual.Actor(window, batch, SPEED_OF_FOOD*random(), 'burger.png')

def create_eater():
	global window
	global batch
	return Visual.Actor(window, batch, SPEED_OF_EATER*random(), 'pacman.png')

def create_neural():
	# на вход сети подаем расстояние до пищи и пожирателей и направление на них
	# на выходе получаем угол поворота и прирост скорости
	#cnt_input = 2*CNT_FOOD + 2*CNT_EATERS - 2
	cnt_input = 2*CNT_FOOD 
	return Neural.MLP(cnt_input, CNT_HIDDEN, 2)


def reset_actors():
	global pacmans
	global hamburgers
	global time

	time = 0.0

	for i in range(CNT_FOOD):
		if hamburgers[i] == None:
			# Восстанавливаем съеденный гамбургер
			hamburgers[i] = create_food()
		else:
			hamburgers[i].reset(SPEED_OF_FOOD*random())
	
	for i in range(CNT_EATERS):
		pacmans[i].reset(SPEED_OF_EATER*random())


def run_neural():
	global time
	global food_label
	global hamburgers
	global pacmans
	global neurals

	# Локальная переменна для подсчета всей съеденной еды
	eaten_food = 0

	for i in range(CNT_EATERS):
		# Для каждого пожирателя перебираем всю еду 
		# подготавливаем входной вектор (input) для нейронной сети
		input = list()

		for j in range(CNT_FOOD):
			if hamburgers[j] == None:			
				# еда уже съедена
				delta_angle, distance = 0.0, 100000.0
				#delta_angle, distance = None, None
			else:	
				# расстояние до еды
				distance = dist(pacmans[i].x - hamburgers[j].x, pacmans[i].y - hamburgers[j].y)
				distance = max(distance, 1)

				# направление к еде
				angle = math.acos( (hamburgers[j].x - pacmans[i].x) / distance )

				# поворок к еде
				if hamburgers[j].y > pacmans[i].y:
					delta_angle = (angle - pacmans[i].angle) % (2*math.pi)
				else:
					delta_angle = (- angle - pacmans[i].angle) % (2*math.pi)

				# видим ли мы под этим углом	
				if VISUAL_ANGLE/2 < delta_angle < 2*math.pi - VISUAL_ANGLE/2:
					distance = 100000.0		
					#distance = None
					delta_angle = 0

				# съедаем ли мы еду	
				if distance <= EAT_DISTANCE:		
					#hamburgers[j] = None 			# еда исчезает
					hamburgers[j] = create_food()	# еда появляется в другом месте
					pacmans[i].inc_food()

			# нормализация значений на промежутке [0,1]		
			#input += [ EAT_DISTANCE / distance, delta_angle / (2.0*math.pi) ]
			input += [ distance / dist(WIDTH, HEIGHT), delta_angle / (2.0*math.pi) ]
	

		# for j in range(CNT_EATERS):
		# 	if i == j:			
		# 		# это сам пожиратель
		# 		angle, distance = 0.0, 100000.0
		# 	else:	
		# 		# расстояние до другого пожирателя
		# 		distance = dist(pacmans[i].x - pacmans[j].x, pacmans[i].y - pacmans[j].y)
		# 		distance = max(distance, 1)

		# 		# направление к еде
		# 		angle = math.acos( (pacmans[j].x - pacmans[i].x) / distance )

		# 		# поворок к еде
		# 		if pacmans[j].y > pacmans[i].y:
		# 			delta_angle = (angle - pacmans[i].angle) % (2*math.pi)
		# 		else:
		# 			delta_angle = (- angle - pacmans[i].angle) % (2*math.pi)

		# 		# видим ли мы под этим углом	
		# 		if VISUAL_ANGLE/2 < delta_angle < 2*math.pi - VISUAL_ANGLE/2:
		# 			distance = 100000.0		

		# 	# нормализация значений на промежутке [0,1]		
		# 	input += [ EAT_DISTANCE / distance, delta_angle / (2.0*math.pi) ]
		
		# Запускаем нейронную сеть пожирателя
		neural = neurals[i]
		output = neural.run(input)

		# Меняем направление и скорость движения пожирателя
		if 0 < pacmans[i].speed + SPEED_OF_EATER/100.0*output[1] < 100*SPEED_OF_EATER:
			pacmans[i].inc_angle_speed(math.pi * output[0], SPEED_OF_EATER/100.0*output[1])
		else:
			# Скорость вышла за пределы - не меняем её
			pacmans[i].inc_angle_speed(math.pi * output[0], 0)

		# Сохраняем информацию о съеденной еде
		eaten_food += pacmans[i].food

	# Выводим инфмормацию о съеденной еде
	food_label.text = 'Food = ' + str(eaten_food)	

	# Запускаем генетический алгоритм
	if eaten_food >= MAX_FOOD:
		next_evolution()


def next_evolution():
	global evolution_num
	global evolution_label
	global pacmans
	global hamburgers
	global neurals

	# Параметры эволюционного алогоритма: особи и их ранги
	persons = list()
	results = list()
	for i in range(CNT_EATERS):
		person = neurals[i].export2vector()
		persons.append(person)
		results.append(pacmans[i].food)
		pacmans[i].food = 0

	# Создание популляции и нового поколения	
	population = Genetic.Population(persons, results)
	superpersons = population.evolution()
	for i in range(CNT_EATERS):
		neurals[i].import_vector(superpersons[i])

	# рекация на создание нового поколения	
	evolution_num += 1	
	evolution_label.text = 'Evolution = ' + str(evolution_num)
	evolution_sound.play()

	reset_actors()


def update(dt):
	global time
	global pacmans
	global hamburgers

	time += dt

	run_neural()

	for i in range(CNT_EATERS):
		pacmans[i].update(dt)

	for i in range(CNT_FOOD):
		if hamburgers[i]: 
			hamburgers[i].update(dt)

	if keymap[pyglet.window.key.SPACE] or time > TIME_TO_RESET:
		reset_actors()


############################################################

# Количество "прогонов" генетического алгоритма
evolution_num = 0

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

evolution_sound = pyglet.resource.media('genetic.wav', streaming=False)

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
for i in range(CNT_EATERS):
	pacmans.append( create_eater() )

hamburgers = list()
for i in range(CNT_FOOD):	
	hamburgers.append( create_food() )

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
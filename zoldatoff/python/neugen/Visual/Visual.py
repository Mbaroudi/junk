#!/usr/bin/python

"""
Visual tools to draw an actor (eater or food)

Sounds were taken from this site: http://www.classicgaming.cc/classics/pacman/sounds.php
"""

import random, math
import pyglet

marginx = 50
marginy = 50


# Draws an eater and moves it in a random direction
class Actor(pyglet.sprite.Sprite):
	"""
	Actor class

	Actor is an image on the screen. It has the following attributes:
	 * position (x, y)
	 * speed
	 * angle 
	 * image

	"""

	def __init__(self, window, batch, speed, image):
		#pass it all on to the superclass constructor http://www.pyglet.org/doc/api/pyglet.sprite.Sprite-class.html
		self.sprite = pyglet.sprite.Sprite.__init__(self, image, batch=batch)

		self.window = window
		self.speed = 0
		self.angle = 0		
		self.scale = 0.5

		self.reborn(speed)


	def reborn(self, speed):
		""" Places an actor in a random place of a window, turns it to a random direction and sets its speed"""
		# place actor in the random place
		self.x = random.uniform(marginx, self.window.width-marginx)
		self.y = random.uniform(marginy, self.window.height-marginy)

		# define a random direction
		self.inc_angle(random.random() * 2.0 * math.pi )

		self.speed = speed


	def inc_angle(self, inc_angle):
		""" Rotates the actor to ``inc_angle`` angle """
		self.angle = (self.angle + inc_angle) % (2.0*math.pi)
		self.rotation = - self.angle*180.0/math.pi
		self.vx, self.vy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed


	def inc_speed(self, inc_speed):
		""" Increases the speed of an actor by ``inc_speed`` """
		self.speed = max(self.speed + inc_speed, 0)		
		self.vx, self.vy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed


	def movement(self, dt):
		""" Calculates new position of an actor after ``dt`` seconds of movement """
		dx = self.vx * dt
		dy = self.vy * dt

		self.x += dx
		self.y += dy


class Eater(Actor):
	""" 
	Eater is an Actor with additional parameters:
	 * eaten food 
	 * moving distance
	 * total rotation (``spin``)
	 * color (more food >> more red)
	 * sound of eating process
	"""

	def __init__(self, window, batch, speed, image):
		super(Eater, self).__init__(window, batch, speed, image)


	def reborn(self, speed):
		""" Sets all properties to zero and calls Actor.__init__() """
		self.food = 0
		self.distance = 0
		self.spin = 0
		super(Eater, self).reborn(speed)
		self.color = (255, 255, 255)


	def inc_food(self, inc_food = 1):
		""" Increases the amount of eaten food by ``inc_food`` """
		self.food += inc_food
		self.color = (255, max(255 - 30 * self.food, 0), max(255 - 30 * self.food, 0))
		self.scale += 0.1


	def inc_angle(self, inc_angle):
		""" Rotates the image of an eater """
		super(Eater, self).inc_angle(inc_angle)
		self.rotation = - self.angle*180.0/math.pi
		self.spin += abs(inc_angle)


	def fitness(self):
		""" Function that calculates the performance of an eater. Fitness will be used in evolution process """
		weight_distance = - 5 / 1e5
		weight_spin = - 2 / 1e4
		return self.food + weight_distance*self.distance + weight_spin*self.spin


	def movement(self, dt):
		""" Calculates new position of an eater after ``dt`` seconds of movement """
		dx = self.vx * dt
		dy = self.vy * dt

		self.distance += math.sqrt(dx*dx + dy*dy) * dt

		self.x += dx
		self.y += dy


class Food(Actor):
	"""
	Food is an actor with special default image
	"""
	def __init__(self, window, batch, speed, image):
		super(Food, self).__init__(window, batch, speed, image)
	

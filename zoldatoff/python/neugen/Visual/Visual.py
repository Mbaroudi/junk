#!/usr/bin/python

import random, math

import pyglet
#from pyglet.gl import *

#velocity = 200 # px per sec

marginx = 50
marginy = 50


# Draws an eater and moves it in a random direction
class Actor(pyglet.sprite.Sprite):
	def __init__(self, window, batch, velocity, image_path):
		self.window = window
		self.velocity = velocity
		self.angle = 0
		self.food = 0

		# load a Pacman image
		image = pyglet.image.load(image_path)

		#centre for rotation and rendering
		image.anchor_x, image.anchor_y = image.width/2, image.height/2

		#pass it all on to the superclass constructor http://www.pyglet.org/doc/api/pyglet.sprite.Sprite-class.html
		self.sprite = pyglet.sprite.Sprite.__init__(self, image, batch=batch)

		self.reset()


	def reset(self):
		# place eater in the random place
		x = random.uniform(marginx, self.window.width-marginx)
		y = random.uniform(marginy, self.window.height-marginy)
		self.set_xy( x, y )

		# define a random direction
		self.set_radian(random.random() * 2.0 * math.pi )


	def set_xy(self, x, y):
		self.x, self.y = x, y	


	# def set_degree(self, degree):
	# 	angle += degree /180 * math.pi 
	# 	self.vx, self.vy = math.cos(angle) * self.velocity, math.sin(angle) * self.velocity


	def set_radian(self, radian):
		self.angle += radian
		self.rotation = - self.angle*180.0/math.pi
		
		self.vx, self.vy = math.cos(self.angle) * self.velocity, math.sin(self.angle) * self.velocity


	def add_food(self):
		self.food += 1


	def update(self, dt):
		x = self.x + self.vx * dt
		y = self.y + self.vy * dt

		if x >= self.window.width-self.image.anchor_x:	# right side
			x = self.x

		if self.x <= self.image.anchor_x:		# left side
			x = self.x

		if self.y >= self.window.height-self.image.anchor_y:	#top
			y = self.y

		if self.y <= self.image.anchor_y:			# bottom
			y = self.y

		self.x = x
		self.y = y



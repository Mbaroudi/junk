#!/usr/bin/python

import random, math
import pyglet

marginx = 50
marginy = 50


# Draws an eater and moves it in a random direction
class Actor(pyglet.sprite.Sprite):
	def __init__(self, window, batch, speed, image_path):
		self.window = window
		self.speed = speed
		self.angle = 0
		self.food = 0

		# load a Pacman image
		image = pyglet.image.load(image_path)

		#centre for rotation and rendering
		image.anchor_x, image.anchor_y = image.width/2, image.height/2

		#pass it all on to the superclass constructor http://www.pyglet.org/doc/api/pyglet.sprite.Sprite-class.html
		self.sprite = pyglet.sprite.Sprite.__init__(self, image, batch=batch)

		self.color=(255, 255, 255)

		self.reset(speed)

		self.sound = pyglet.resource.media('pacman.wav', streaming=False)


	def reset(self, speed):
		# place eater in the random place
		x = random.uniform(marginx, self.window.width-marginx)
		y = random.uniform(marginy, self.window.height-marginy)
		self.set_xy( x, y )

		# define a random direction
		self.inc_angle(random.random() * 2.0 * math.pi )

		self.speed = speed

		self.color = (255, max(255 - 30 * self.food, 0), max(255 - 30 * self.food, 0))


	def set_xy(self, x, y):
		self.x, self.y = x, y	


	def set_rgb(self, r, g, b):
		self.color=(r, g, b)

	# def set_speed(self, speed):
	# 	self.speed = speed

	def inc_angle(self, inc_angle):
		self.angle = (self.angle + inc_angle) % (2.0*math.pi)
		self.rotation = - self.angle*180.0/math.pi
		
		self.vx, self.vy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed

	def inc_angle_speed(self, inc_angle, inc_speed):
		self.angle = (self.angle + inc_angle) % (2.0*math.pi)
		self.rotation = - self.angle*180.0/math.pi

		self.speed = max(self.speed + inc_speed, 0)
		
		self.vx, self.vy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed

	def inc_food(self):
		self.food += 1
		self.color = (255, max(255 - 30 * self.food, 0), max(255 - 30 * self.food, 0))
		self.sound.play()


	def update(self, dt):
		x = self.x + self.vx * dt
		y = self.y + self.vy * dt

		# if x >= self.window.width-self.image.anchor_x:	# right side
		# 	x = self.x

		# if self.x <= self.image.anchor_x:		# left side
		# 	x = self.x

		# if self.y >= self.window.height-self.image.anchor_y:	#top
		# 	y = self.y

		# if self.y <= self.image.anchor_y:			# bottom
		# 	y = self.y

		self.x = x
		self.y = y



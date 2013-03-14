#!/usr/bin/python

# Sounds were taken from this site: http://www.classicgaming.cc/classics/pacman/sounds.php

import random, math
import pyglet

marginx = 50
marginy = 50


# Draws an eater and moves it in a random direction
class Actor(pyglet.sprite.Sprite):
	def __init__(self, window, batch, speed, image_path):
		self.window = window
		self.speed = 0
		self.angle = 0		

		# load a Pacman image
		image = pyglet.image.load(image_path)

		#centre for rotation and rendering
		image.anchor_x, image.anchor_y = image.width/2, image.height/2

		#pass it all on to the superclass constructor http://www.pyglet.org/doc/api/pyglet.sprite.Sprite-class.html
		self.sprite = pyglet.sprite.Sprite.__init__(self, image, batch=batch)

		self.scale = 0.5

		self.reborn(speed)


	def reborn(self, speed):
		# place eater in the random place
		self.x = random.uniform(marginx, self.window.width-marginx)
		self.y = random.uniform(marginy, self.window.height-marginy)

		# define a random direction
		self.inc_angle(random.random() * 2.0 * math.pi )

		self.speed = speed


	def inc_angle(self, inc_angle):
		self.angle = (self.angle + inc_angle) % (2.0*math.pi)
		self.rotation = - self.angle*180.0/math.pi
		self.vx, self.vy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed


	def inc_speed(self, inc_speed):
		self.speed = max(self.speed + inc_speed, 0)		
		self.vx, self.vy = math.cos(self.angle) * self.speed, math.sin(self.angle) * self.speed


	def movement(self, dt):
		dx = self.vx * dt
		dy = self.vy * dt

		self.x += dx
		self.y += dy


class Eater(Actor):
	def __init__(self, window, batch, speed, image_path='pacman.png'):
		self.food = 0
		self.distance = 0
		self.spin = 0
		super(Eater, self).__init__(window, batch, speed, image_path)

		self.color = (255, 255, 255)
		self.sound = pyglet.resource.media('pacman.mp3', streaming=False)

	def reborn(self, speed):
		super(Eater, self).reborn(speed)
		self.color = (255, max(255 - 30 * self.food, 0), max(255 - 30 * self.food, 0))

	def inc_food(self, inc_food = 1):
		self.food += 1
		self.color = (255, max(255 - 30 * self.food, 0), max(255 - 30 * self.food, 0))
		self.scale += 0.1
		self.sound.play()

	def inc_angle(self, inc_angle):
		super(Eater, self).inc_angle(inc_angle)
		self.rotation = - self.angle*180.0/math.pi
		self.spin += abs(inc_angle)

	def set_rgb(self, r, g, b):
		self.color=(r, g, b)

	def fitness(self):
		weight_distance = - 5 / 1e5
		weight_spin = - 2 / 1e4
		return self.food + weight_distance*self.distance + weight_spin*self.spin

	def movement(self, dt):
		dx = self.vx * dt
		dy = self.vy * dt

		self.distance += math.sqrt(dx*dx + dy*dy) * dt

		self.x += dx
		self.y += dy


class Food(Actor):
	def __init__(self, window, batch, speed, image_path='food.png'):
		super(Food, self).__init__(window, batch, speed, image_path)
	

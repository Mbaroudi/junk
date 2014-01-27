#!/usr/bin/env python
#coding: utf-8

# Задача коммивояжёра
# Алгоритм отжига
# http://habrahabr.ru/post/209610/

from config import *
from time import time
from random import random, seed
from math import sqrt, pow, exp
from PIL import Image,ImageDraw


def energy(towns):
	e = 0

	for i in range(len(towns)):	
		p1 = towns[i]

		if i > 0:	
			p2 = towns[i-1]
		else:
			p2 = towns[len(towns)-1]

		e += sqrt( pow(p1[0]-p2[0], 2) + pow(p1[1]-p2[1], 2) )

	return e



def mutate_towns(towns):
	l = len(towns) - 1
	n1 = int(round(l*random()))
	n2 = int(round(l*random()))
	#print 'n1', n1
	#print 'n2', n2

	if n1 < n2:
		towns[n1:n2] = reversed(towns[n1:n2])
	else:
		towns[n2:n1] = reversed(towns[n2:n1])

	return towns

def draw(towns, filename='00.png', w=500, h=500):
	def town2xy(town, w, h):
		x = w * 0.1 + town[0] * 0.8 * w
		y = h * 0.1 + town[1] * 0.8 * h
		return (x, y)

	img=Image.new('RGB', (w,h), (255,255,255))
	draw=ImageDraw.Draw(img)

	for i in range(len(towns)):
		p1 = town2xy(towns[i], w, h)

		if i > 0:	
			p2 = town2xy(towns[i-1], w, h)			
		else:
			p2 = town2xy(towns[len(towns)-1], w, h)  

		draw.line( (p1[0],p1[1],p2[0],p2[1]), fill=(255,0,0) )    
		draw.ellipse( [p1[0]-2, p1[1]-2, p1[0]+2, p1[1]+2], fill=(0,0,255) )    

	draw.text( (0.1 * w, 0.9 * h), str(round(energy(towns), 2)), (0,0,0) ) 

	img.save(filename,'PNG')


seed(time())
towns = [(random(), random()) for i in range(CNT_TOWNS)]
draw(towns)

t = Tmax
i = 1

while t > Tmin:
	#print '==============='
	#print 'loop #', i
	towns1 = list(towns)
	e1 = energy(towns1)
	towns2 = mutate_towns(towns1)
	e2 = energy(towns2)

	if e2 < e1:
		towns = towns2
		#print 'energy', e2

	if e2 >= e1 and random() < exp( (e1-e2) / t ):
		towns = towns2		
		#print 'energy', e2

	i = i + 1
	t = 1.0 * Tmax / i
	#print 'T', t

	#if i > MAX_ITERATIONS:
	#	break

draw(towns, '01.png')

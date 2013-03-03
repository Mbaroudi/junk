#!/usr/bin/python

from random import random, uniform
from math import log

def randomindex(pexp=0.7):
		return int( log(random()) / log(pexp) )

def mutate(person, probability=0.05):
	mutant = list()
	for i in range(len(person)):
		if random() < probability:
			mutant.append(uniform(-1.0, 1.0))
		else:
			mutant.append(person[i])

	return mutant

class Population():
	def __init__(self, persons, results):
		self.persons = persons
		self.results = results
		self.len = min(len(self.persons), len(self.results))

	def __del__(self):
		None


	def crossover(self, p1, p2, probswap=0.7):
		person1 = self.persons[p1]
		person2 = self.persons[p2]
		person = list()

		for i in range(len(person1)):
			if random() < probswap:
				person.append(person1[i])
			else:
				person.append(person2[i])

		return person


	def sort(self):
		sortlist = list()
		for i in range(self.len):
			tup = (self.results[i], self.persons[i])
			sortlist.append(tup)
		sortlist.sort(key=lambda tup: tup[0])
		self.persons = [sortlist[i][1] for i in range(self.len)]


	def evolution(self, cnt_elite=2):
		sortlist = self.sort()
		superpersons = list()

		for i in range(cnt_elite):
			superpersons.append(self.persons[i])

		for i in range(self.len-cnt_elite):
			p1 = randomindex()
			p2 = randomindex()
			person = self.crossover(p1, p2)
			superpersons.append(mutate(person))

		return superpersons	





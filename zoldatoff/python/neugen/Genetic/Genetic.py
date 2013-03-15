#!/usr/bin/python

"""
Implementation of genetic algorythm
"""

from random import random, uniform
from math import log


def randomindex(pexp=0.7):
	""" Returns non-uniform random value (more probable to obtain lesser value) """
	return int( log(random()) / log(pexp) )


def mutate(person, probability=0.02):
	""" 
	Mutation

	Every chromosome of a person mutates with probability ``probability``
	"""
	mutant = list()
	for i in range(len(person)):
		if random() < probability:
			mutant.append(uniform(-2.0, 2.0))
		else:
			mutant.append(person[i])

	return mutant


class Population():
	"""
	Implementation of a genetic algorythm

	 * Population consists of ``persons``. 
	 * Every person consists of chromosomes.
	 * Persons are ranged by ``results``

	During the evolution process:
	 * Several best (elite) persons of the population become ``superpersons`` without changes
	 * Persons crossover and produce new ``superpersons`` after mutation 
	"""
	def __init__(self, persons, results):
		self.persons = persons
		self.results = results
		self.len = min(len(self.persons), len(self.results))

		self.sort()

	def crossover(self, p1, p2, probswap=0.8):
		""" 
		Crossover process
		
		Every chromosome of the new person is equal to the chromosome of peron ``p1``
		with probability ``probswap``
		"""
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
		""" Sort the persons by their results """ 
		sortlist = [ (self.results[i], self.persons[i]) for i in range(self.len) ]
		sortlist.sort(key=lambda sl: sl[0], reverse=True)

		self.results = [sortlist[i][0] for i in range(self.len)]
		self.persons = [sortlist[i][1] for i in range(self.len)]

	def evolution(self, cnt_elite=2):
		"""
		Evolution process

		``superpersons`` are:
		 * ``cnt_elite`` best persons of original population
		 * result of crossover and mutation of random persons from original population
		"""
		superpersons = [ self.persons[i] for i in range(cnt_elite) ]

		for i in range(self.len-cnt_elite):
			p1 = min(randomindex(), self.len-1)
			p2 = min(randomindex(), self.len-1)
			person = self.crossover(p1, p2)
			superpersons.append(mutate(person))

		return superpersons	





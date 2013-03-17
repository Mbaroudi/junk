#!/usr/bin/python

"""
Neural network implementation
"""

from math import tanh, exp
from random import seed, uniform


def sigmoid(x):
	"""
	Sigmoid function

	Activation funtion of a neuron
	"""
	alpha = 1.5
	if x < -30:
		sig = 0
	elif x > 30:
		sig = 1
	else:
		sig = 1.0 / ( 1.0 + exp(-alpha*x) )
	return (sig - 0.5) * 2.0


class Neuron():
	"""
	Neuron

	Neuron consists of:
	 * Inputs. Number of inputs is  ``cnt_input``. Every input has its weight
	 * Activation function
	 * A single output
	"""

	def __init__(self, cnt_input):

		self.cnt_input = 0 
		self.weight_input = list()
		
		seed()

		for i in range(cnt_input):
			self.add_input()

		self.set_func()


	def set_func(self, func=sigmoid):
		""" Set activation function """
		self.func = func


	def add_input(self):
		""" Add a new input with random weight to the neuron """
		self.cnt_input += 1
		self.weight_input.append( uniform(-1.0, 1.0) )


	def run(self, input):
		""" 
		Activate the neuron using ``input`` signal

		Every input is activated and multiplied by its weight.
		The sum of these signals is affected by activation function and sent to output
		"""
		sum = 0.0
		for i in range(self.cnt_input):
			if input[i] != None and self.weight_input[i] != None:
				sum += input[i] * self.weight_input[i]

		return self.func(sum)


	def export2vector(self):
		""" Exports input weights to a list """
		return self.weight_input


	def import_vector(self, vector):
		""" Imports input weights from a list ``vector`` """
		self.weight_input = vector
		self.cnt_input = len(vector)



class MLP(Neuron):
	"""
	Multilayer perceptron

	Consists of:
	 * inputs
	 * hidden layer of neurons
	 * output layer of neurons
	"""

	def __init__(self, cnt_input, cnt_hidden, cnt_output=1): 
		
		self.cnt_input  = cnt_input
		self.cnt_hidden = cnt_hidden
		self.cnt_output = cnt_output

		self.hidden = [ Neuron(cnt_input) for i in range(self.cnt_hidden) ]
		self.output = [ Neuron(cnt_hidden) for i in range(self.cnt_output) ]


	def add_input(self):
		""" Adds new input to neural network """
		self.cnt_input += 1
		for i in range(self.cnt_hidden):
			neuron = self.hidden[i]
			neuron.add_input()


	def add_hidden(self):
		""" Adds new hidden-layer neuron to neural network """
		self.cnt_hidden += 1
		neuron = Neuron(self.cnt_input)
		self.hidden.append(neuron)


	def run(self, input):
		""" Calculate output signal using input signal and neurons """
		hidden_output = list()
		for i in range(self.cnt_hidden):
			neuron = self.hidden[i]
			hidden_output.append(neuron.run(input))

		output = list()
		for i in range(self.cnt_output):
			neuron = self.output[i]
			output.append(neuron.run(hidden_output))

		return output


	def export2vector(self):
		""" Export the neurons' weights to a list """
		vector = list()
		for neuron in self.hidden:
			vector += neuron.export2vector()
		for neuron in self.output:
			vector += neuron.export2vector()

		return vector


	def import_vector(self, vector):
		""" Import neurons' weights from a list ``vector``"""
		for i in range(self.cnt_hidden):
			neuron_vector = vector[i*self.cnt_input : (i+1)*self.cnt_input]
			self.hidden[i].import_vector(neuron_vector)

		for i in range(self.cnt_output):
			neuron_vector = vector[self.cnt_hidden*self.cnt_input + i*self.cnt_hidden : self.cnt_hidden*self.cnt_input + (i+1)*self.cnt_hidden]
			self.output[i].import_vector(neuron_vector)






#!/usr/bin/python

from math import tanh, exp
import random
#from pysqlite2 import dbapi2 as sqlite

def sigmoid(x):
	alpha = 1.0
	sig = 1.0 / ( 1.0 + exp(-alpha*x) )
	return (sig - 0.5) * 2.0

class Neuron():
	def __init__(self, cnt_input):

		self.cnt_input = 0 #cnt_input
		self.weight_input = list()
		
		random.seed()

		for i in range(cnt_input):
			self.add_input()

		self.set_func()


	def set_func(self, func=sigmoid):
		self.func = func


	def add_input(self):
		self.cnt_input += 1
		self.weight_input.append( random.uniform(-1.0, 1.0) )
		return self.cnt_input


	def run(self, input):
		sum = 0.0
		for i in range(self.cnt_input):
			if input[i] != None and self.weight_input[i] != None:
				sum += input[i] * self.weight_input[i]
				#print str(i) + ' ' + str(input[i]) + ' ' + str(self.weight_input[i])

		return self.func(sum)

	def export2vector(self):
		return self.weight_input

	def import_vector(self, vector):
		print vector
		self.weight_input = vector
		self.cnt_input = len(vector)

	def train(self):
		None




class MLP(Neuron):
	def __init__(self, cnt_input, cnt_hidden, cnt_output=1): 
		#self.con = sqlite.connect(dbname)
		
		self.cnt_input = cnt_input
		self.cnt_hidden = cnt_hidden
		self.cnt_output = cnt_output

		self.hidden = list()
		for i in range(self.cnt_hidden):
			neuron = Neuron(cnt_input)
			#neuron.set_func(tanh)
			self.hidden.append(neuron)

		self.output = list()	
		for i in range(self.cnt_output):
			neuron = Neuron(cnt_hidden)
			#neuron.set_func(tanh)
			self.output.append(neuron)


	def __del__(self):
		#self.con.close()
		None

	def db_maketables(self):
		self.con.execute('create table hiddennode(create_key)')
		self.con.execute('create table input2hidden(mplid, inputid, hiddenid, weight')
		self.con.execute('create table hidden2output(mplid, hiddenid, outputid, weight')
		self.con.commit()


	def add_input(self):
		self.cnt_input += 1
		for i in range(self.cnt_hidden):
			neuron = self.hidden[i]
			neuron.add_input()

		return self.cnt_input


	def add_hidden(self):
		self.cnt_hidden += 1
		neuron = Neuron(self.cnt_input)
		#neuron.set_func(tanh)
		self.hidden.append(neuron)

		return self.cnt_hidden


	def run(self, input):
		hidden_output = list()
		for i in range(self.cnt_hidden):
			neuron = self.hidden[i]
			hidden_output.append(neuron.run(input))

		output = list()
		for i in range(self.cnt_output):
			neuron = self.output[i]
			output.append(neuron.run(hidden_output))


		# print input	
		# print hidden_output
		# print output	
		# print "----"

		return output


	def propagate(self):
		None

	def export2db(self):
		None

	def load_db(self):
		None

	def export2vector(self):
		vector = list()
		for neuron in self.hidden:
			vector.append(neuron.export2vector())
		for neuron in self.output:
			vector.append(neuron.export2vector())
		return vector

	def import_vector(self, vector):
		for i in range(self.cnt_hidden):
			neuron_vector = vector[i*self.cnt_input : (i+1)*self.cnt_input-1]
			self.hidden[i].import_vector(neuron_vector)

		for i in range(self.cnt_output):
			neuron_vector = vector[self.cnt_hidden*self.cnt_input + i*self.cnt_hidden : self.cnt_hidden*self.cnt_input + (i+1)*self.cnt_hidden-1]
			self.output[i].import_vector(neuron_vector)


#mlp = MLP(5, 5, 1)
#input = [1,2,3,4,5]
#print mlp.run(input)





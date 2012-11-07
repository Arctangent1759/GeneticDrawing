#################
#    Imports    #
#################
import tkinter
import random
import math

#################
#Utility Functions
#################

def prob_sim(probability):
	"""Simulates a random event."""
	assert 0<=probability<=1
	return random.random()<=probability


#################
#Genetic Classes#
#################

class Instruction(object):
	"""Defines a geometric action."""
	def __init__(self, length, heading, color, radians='radians'):
		"""
		Creates an instruction.
		@param length: How far the brush moves relative to the endpoint of the previous instruction.
		@param heading: Heading relative to the heading of the previous instruction.
		@param color: Color of the stroke.
		"""
		self.length=length
		self.heading=heading if radians=='radians' else math.radians(heading)
		self.color=color
		
	def execute(self,brush):
		"""Executes the instruction."""
		pass
	
class Allele(object):
	"""An Allele defines a sequence of instructions."""
	def __init__(self, instruction_list):
		self.instructions=instruction_list
		
	def execute(self,brush):
		"""Executes the instructions on the allele."""
		for instruction in self.instructions:
			instruction.execute(brush)

class Chromosome(object):
	"""A Chromosome is an unordered collection of Alleles."""
	CROSSOVER_CHANCE=.2
	
	def __init__(self, gene_list):
		self.genes=gene_list
				
	def execute(self,brush):
		for gene in self.genes:
			gene.execute(brush)
			
	def __len__(self):
		return len(self.genes)
			
	@staticmethod
	def crossover(c1,c2):
		"""Genetic Crossover between two chromosomes; randomly interchanges alleles."""
		assert len(c1) == len(c2), 'Chromosome lengths not equal!'
		for i in range(len(c1)):
			if prob_sim(Chromosome.CROSSOVER_CHANCE):
				c1.genes[i],c2.genes[i]=c2.genes[i],c1.genes[i]



###################
#Graphical Classes#
###################
cvs=tkinter.Canvas(tkinter.Tk(),width=1000,height=1000)
cvs.pack()

class Brush(object):
	def __init__(self,x,y,cvs):
		self.x=x
		self.y=y
		self.heading=0
		self.cvs=cvs
	
	def execute(self,instruction):
		new_x=self.x+instruction.length*math.cos(instruction.heading+self.heading)
		new_y=self.y+instruction.length*math.sin(instruction.heading+self.heading)
		self.cvs.create_line(self.x,self.y,new_x,new_y,fill=instruction.color)
		self.heading+=instruction.heading
		self.x=new_x
		self.y=new_y

brush=Brush(100,100,cvs)

brush.execute(Instruction(100,0,'red'))
print(brush.heading)
brush.execute(Instruction(100,120,'green'))
print(brush.heading)
brush.execute(Instruction(100,120,'blue'))
print(brush.heading)

input()
#################
#    Imports    #
#################
import tkinter
import random
import math
from copy import deepcopy

#################
#   Constants   #
#################
SIMWIDTH=600
SIMHEIGHT=600
BGCOLOR="BLACK"
MAX_INSTRUCTION_DISTANCE=100
MAX_DOMINANCE=3
MAX_GENE_LENGTH=5
INIT_CHROMOSOME_LENGTH=5
INIT_POPULATION_SIZE=20


#################
#Utility Functions
#################

def prob_sim(probability):
	"""Simulates a random event."""
	assert 0<=probability<=1, 'Invalid probability.'
	return random.random()<=probability

def rand_color():
	return "#{0}{1}{2}".format(hex(random.randint(0,15))[2:],hex(random.randint(0,15))[2:],hex(random.randint(0,15))[2:])

#################
#Genetic Classes#
#################

class Instruction(object):
	"""Defines a geometric action."""
	MAX_LENGTH_CHANGE=30
	MAX_HEADING_CHANGE=math.radians(30)
	def __init__(self, length, heading, color, angtype='degrees'):
		"""
		Creates an instruction.
		@param length: How far the brush moves relative to the endpoint of the previous instruction.
		@param heading: Heading relative to the heading of the previous instruction.
		@param color: Color of the stroke.
		@param angtype: Specifies the type of angle in the input.
		"""
		self.length=length
		self.heading=heading if angtype=='radians' else math.radians(heading)
		self.color=color
		
	def execute(self,brush):
		"""Executes the instruction."""
		brush.execute(self)
		
	def mutate(self):
		self.length+=(1 if prob_sim(.5) else -1)*(random.random())*(self.MAX_LENGTH_CHANGE)
		if self.length<0:
			self.length=0
		self.heading+=(1 if prob_sim(.5) else -1)*(random.random())*(self.MAX_HEADING_CHANGE)
		self.color=rand_color()

	def __str__(self):
		return "\n---------------------\nlength: {0}\nheading: {1} degrees\ncolor: {2}\n---------------------\n".format(self.length,math.degrees(self.heading),self.color)
	
	def __repr__(self):
		return "Instruction({0},{1},{2})".format(self.length,math.degrees(self.heading),self.color)
	
class Allele(object):
	CHANGE_DOMINANCE_CHANCE=0.7
	
	"""An Allele defines a sequence of instructions."""
	def __init__(self, instruction_list, dominance):
		self.instructions=instruction_list
		self.dominance=dominance
		
	def execute(self,brush):
		"""Executes the instructions on the allele."""
		for instruction in self.instructions:
			instruction.execute(brush)
	
	def mutate(self):
		for instruction in self.instructions:
			instruction.mutate()
		if prob_sim(self.CHANGE_DOMINANCE_CHANCE):
			self.dominance+=1 if prob_sim(.5) else -1
			if self.dominance < 0:
				self.dominance=0
			elif self.dominance > MAX_DOMINANCE:
				self.dominance=MAX_DOMINANCE
			
	def __str__(self):
		out=""
		for instruction in self.instructions:
			out+=str(instruction)
		return "====================\n{0}-dominance allele\n\nInstructions:\n".format(self.dominance)+out+"\n====================="
	
	def __repr__(self):
		return "Allele({0},{1})".format(self.instructions,self.dominance)

class Chromosome(object):
	"""A Chromosome is an unordered collection of Alleles."""
	
	def __init__(self, gene_list):
		self.genes=gene_list
			
	def __len__(self):
		return len(self.genes)
	
	def transposon(self):
		self.genes.append(deepcopy(self.genes[random.randint(0,len(self)-1)]))
		
	def mutate(self):
		for gene in self.genes:
			gene.mutate()

class Chromosome_Pair(object):
	"""Two Homologous Chromosomes"""
	CROSSOVER_CHANCE=.2
	GROWTH_CHANCE=.2
	MUTATION_CHANCE=.2
	def __init__(self,c1,c2):
		self.length= min(len(c1),len(c2))
		self.c1=c1
		self.c2=c2
	
	def __len__(self):
		return self.length
	
	def crossover(self):
		"""Genetic Crossover between two chromosomes; randomly interchanges alleles."""
		for i in range(len(self)):
			if prob_sim(self.CROSSOVER_CHANCE):
				self.c1.genes[i],self.c2.genes[i]=self.c2.genes[i],self.c1.genes[i]

	def execute(self,brush):
		for i in range(len(self)):
			if self.c1.genes[i].dominance>self.c2.genes[i].dominance:
				self.c1.genes[i].execute(brush)
			elif self.c2.genes[i].dominance>self.c1.genes[i].dominance:
				self.c2.genes[i].execute(brush)
			else:
				self.c1.genes[i].execute(brush)
				
	def mutate(self):
		if prob_sim(self.GROWTH_CHANCE):
			self.c1.transposon()
			self.c2.transposon()
		if prob_sim(self.MUTATION_CHANCE):
			self.c1.mutate()
		if prob_sim(self.MUTATION_CHANCE):
			self.c2.mutate()
				
	@staticmethod
	def recombine(cp1,cp2):
		roll=random.random()
		if roll<.25:
			return Chromosome_Pair(cp1.c1,cp2.c1)
		elif roll<.5:
			return Chromosome_Pair(cp1.c2,cp2.c1)
		elif roll <.75:
			return Chromosome_Pair(cp1.c1,cp2.c2)
		else:
			return Chromosome_Pair(cp1.c2,cp2.c2)

class Individual(object):
	def __init__(self,chromosome_pair, brush):
		self.dna=chromosome_pair
		self.brush=brush
		self.rating=0
		
	def execute(self):
		self.dna.execute(self.brush)
	
	@staticmethod
	def mate(individual1,individual2):
		dna1=(deepcopy(individual1.dna))
		dna2=(deepcopy(individual2.dna))
		dna1.crossover()
		dna2.crossover()
		newcp=Chromosome_Pair.recombine(dna1,dna2)
		newcp.mutate()
		return Individual(newcp,brush)

###################
#Graphical Classes#
###################

class Brush(object):
	def __init__(self,x,y,cvs):
		self.ox=x
		self.oy=y
		self.x=x
		self.y=y
		self.heading=0
		self.cvs=cvs
		
	def reset(self):
		self.x=self.ox
		self.y=self.oy
		self.heading=0
		self.cvs.create_rectangle(0,0,SIMWIDTH,SIMHEIGHT,fill=BGCOLOR)
		
	def clear(self):
		self.reset()
		
	
	def execute(self,instruction):
		new_x=self.x+instruction.length*math.cos(instruction.heading+self.heading)
		new_y=self.y+instruction.length*math.sin(instruction.heading+self.heading)
		self.cvs.create_line(self.x,self.y,new_x,new_y,fill=instruction.color)
		self.heading=self.heading+instruction.heading
		self.x=new_x
		self.y=new_y

##################
# Graphical Init #
##################

cvs=tkinter.Canvas(tkinter.Tk(),width=SIMWIDTH,height=SIMHEIGHT)
cvs.pack()
brush=Brush(SIMWIDTH/2,SIMHEIGHT/2,cvs)
brush.clear()

###################
#Simulation Functions
###################

def rand_instr():
	return Instruction(random.randint(0,MAX_INSTRUCTION_DISTANCE),random.randint(0,360),rand_color())

def rand_allele(gene_length):
	instrlist=[]
	for _ in range(gene_length):
		instrlist.append(rand_instr())
	return Allele(instrlist,random.randint(0,MAX_DOMINANCE))

def rand_chromosome(length):
	allelelist=[]
	for _ in range(length):
		allelelist.append(rand_allele(random.randint(0,random.randint(0,MAX_GENE_LENGTH))))
	return Chromosome(allelelist)

def rand_individual():
	return Individual(Chromosome_Pair(rand_chromosome(INIT_CHROMOSOME_LENGTH),rand_chromosome(INIT_CHROMOSOME_LENGTH)),brush)
		
###################
#   Simulation    #
###################

#Populate the world with random individuals
population=[]
for _ in range(INIT_POPULATION_SIZE):
	population.append(rand_individual)


while True: #Main loop
	stdev=0
	total=0
	mean=0
	for individual in population: #Selection. Have the user rate each individual.
		brush.clear()
		individual.execute()
		individual.rating=input()



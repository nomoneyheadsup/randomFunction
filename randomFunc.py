import sys
import time

from output import *
from variables import *
from control import *
from control import _PutCodeControlSpark

# TODO: reference some volatiles to avoid optimization
#         --> can replace these with jmps to middle of instructions
# TODO: place some dummy calls to later replace with jmp's

# writes text to a stored outputString
# fetch the outputString later for outputting
	
class Function:
	totalFuncCounter = 0
	
	def __init__(self, output = None, globalVars = None):
		self.funcNum = Function.totalFuncCounter
		Function.totalFuncCounter += 1
		
		if globalVars is None:
			self.variables = Variables(random.randint(4, 9))
		else:
			self.variables = Variables(random.randint(4, 9), globalVars)
			
		if output is None:
			self.out = Output()
		else:
			self.out = output
		self.name = 'RandFunc' + str(self.funcNum)
		self.labels = Labels()
		#self.action = Action(self.variables, self.out)
		
	def __FunctionHeader(self):
		self.out.output('int ' + self.name + '()')
		self.out.line()
		self.out.output('{')
		self.out.line()
		
	def __FunctionFooter(self):
		retval = self.variables.Rand()
		self.out.output('return ' + retval + ';')
		self.out.line()
		self.out.output('}')
		self.out.line()
		
	def __ResolveGotos(self):
		try:
			self.out.outputString = self.labels.ResolveGotos(self.out.outputString)
		except ZeroLabelsException:
			pass
	
	def __Generate(self):		
		# int functionname()
		# {
		self.__FunctionHeader()
		
		# int a = 1, b = 2, etc
		self.variables.InitStatement(self.out)
		
		# [function body]
		_PutCodeControlSpark(self.out, self.variables, self.labels).Exec()
		
		# return a;
		self.__FunctionFooter()
		
		self.__ResolveGotos()
		
	def Generate(self, minLines = None):
		if minLines == None:
			minLines = 1 # < 1 will cause errors
		
		# to achieve minLines, we generate new functions from scratch until achieved
		while self.out.lineCount < minLines or self.labels.labelCount == 0:
			self.out.Clear()
			self.labels.Clear()
			self.__Generate()
	
	def GetCode(self):
		return self.out.outputString
	
class Project:
	def __init__(self):
		self.functions = []
		self.out = Output()

		self.volatiles = VolVariables(random.randint(3, 7))
		self.volatiles.InitStatement(self.out)
		
	def AddFunction(self):
		func = Function(globalVars = self.volatiles)
		func.Generate(minLines = 30)
		self.functions.append(func)		
		
	def AddFunctions(self, count):
		for x in range(count):
			self.AddFunction()
			
	def GetFullCode(self):
		buf = self.out.outputString
		funcs = [func.GetCode() for func in self.functions]
		buf += ('\n'.join(funcs))
		return buf
	
def PrintLongFunction():
	proj = Project()
	proj.AddFunctions(3)
	code = proj.GetFullCode()
	sys.stdout.write(code)
	
if __name__ == "__main__":
	benchmark =  0
	
	startTime = time.time()
	PrintLongFunction()
	
	benchmark = time.time() - startTime
	sys.stdout.write('\n//Benchmark: ' + str(benchmark))
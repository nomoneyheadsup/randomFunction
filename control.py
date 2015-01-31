import random
from modWeighted import weightedSample
		
class ControlSelector:
	@staticmethod
	def RandomControl(output, variables, labels, nestingLevel):
		choices = {ControlType.STATEMENT: 30,
				   ControlType.CONDITIONAL: 6, 
				   ControlType.GOTO: 2,
				   ControlType.STOP: 7,
				   ControlType.APICALL: 1 }
		
		choices[ControlType.STOP] += 3 ** nestingLevel
		
		choiceList = list(choices.items())
		[controlType,] = weightedSample(choiceList, 1)
		return ControlType.Make(controlType, output, variables, labels)

class ControlType:
	STATEMENT = 1
	CONDITIONAL = 2
	GOTO = 3
	GENCALL = 4
	REALCALL = 5
	APICALL = 6
	STOP = 7
	IO = 8
	allTypes = [STATEMENT, CONDITIONAL, GOTO, GENCALL, REALCALL, APICALL, STOP, IO]
	implementedTypes = [STATEMENT, CONDITIONAL, GOTO, STOP]
	
	@staticmethod
	def Make(controlType, output, variables, labels): # factory pattern .. I think
		if(controlType ==  ControlType.STATEMENT):
			return StatementControl(output, variables, labels)
		elif(controlType ==  ControlType.CONDITIONAL):
			return ConditionalControl(output, variables, labels)
		elif(controlType ==  ControlType.STOP):
			return StopControl(output, variables, labels)
		elif(controlType == ControlType.GOTO):
			return GotoControl(output, variables, labels)
		elif(controlType == ControlType.APICALL):
			return ApiCallControl(output, variables, labels)
		else:
			raise Exception('b-b-baka!')
		
	def __init__(self, output, variables, labels, nestingLevel = 0):
		self.out = output
		self.variables = variables
		self.labels = labels
		self.nestingLevel = nestingLevel
		
	def Exec(self):
		raise NotImplementedError("")
	
	def PutCode(self):
		shouldContinue = True
		
		while shouldContinue:
			control = ControlSelector.RandomControl(self.out, self.variables, self.labels, self.nestingLevel + 1)
		
			shouldContinue = control.Exec()
			
# Should be used only once per function generation
class _PutCodeControlSpark(ControlType):
	def Exec(self):
		self.PutCode()
	
class StatementControl(ControlType):
	def PutLabel(self):
		self.out.output(self.labels.CreateNew() + ':')
		self.out.line()
		
	def DivOperand(self):
		return random.choice([2, 4, 8, 16, self.variables.constants.GetConstant()])
	
	def MultiOperand(self):
		return random.choice([2, 3, 4, 5, 6, 8, 10, 16, self.variables.constants.GetConstant()])
	
	def ArithOperand(self):
		return random.choice([1, 1, 2, 4, 8, 10, 16, 32, 64, self.variables.constants.GetConstant()])
	
	def ModOperand(self):
		return random.choice([2, 2, 2, 4, 8, random.randint(2, 20), self.variables.constants.GetConstant()])
	
	def MapOperand(self, op):
		d = {'+': self.ArithOperand, '-': self.ArithOperand, '*': self.MultiOperand, '/' : self.DivOperand, '%' : self.ModOperand}
		return d[op]()
		
	def ModifyVar(self, var):
		r = random.randint(1, 15)
		if 1 <= r <= 4:
			return var
		elif 5 <= r <= 14:
			op = random.choice(['+', '-', '*', '/', '%'])
			return var + ' ' + op + ' ' + str(self.MapOperand(op))
		else:
			return var + ' << ' + str(random.randint(2, 30))
	
	def PutAssignment(self):
		dest, src = self.variables.Rand(2, globalChance = 0.30)
		self.out.output(dest + ' = ' + self.ModifyVar(src) + ';')
		self.out.line()		
	
	def Exec(self):
		r = random.randint(1, 5)
		if r == 1:
			self.PutLabel()
			
		self.PutAssignment()

		return True
			
class GotoControl(ControlType):
	def PutGoto(self):
		self.out.output('goto ' + '%INSERTLABEL%' + ';')
		self.out.line()	
	
	def Exec(self):
		self.PutGoto()
		return False
	
class ConditionalControl(ControlType):
	def _Comparison(self):
		conditions = ['==', '<', '>', '<=', '>=', '!=']
		return random.choice(conditions)
	
	def PutConditional(self):
		# TODO:
		# EXPR can be
		#   == between two vars with modifiers
		#   WINAPI call
		#   call to another gen function (or real function?)
		first, second = self.variables.RandCond(2, globalChance = 0.10)
		self.out.output('(')
		self.out.output(first + ' ' + self._Comparison() + ' ' + second)
		self.out.output(')')
	
	def PutBlock(self):
		self.out.output('{')
		self.out.line()
		self.out.incNesting()
		self.PutCode()
		self.out.decNesting()
		self.out.output('}')
		self.out.line()
	
	def PutIf(self):
		self.out.output('if')
		self.PutConditional()
		self.PutBlock()
		
	def PutElseIf(self):
		self.out.output('else if')
		self.PutConditional()
		self.PutBlock()
		
	def PutElse(self):
		self.out.output('else')
		self.PutBlock()	
	
	def Exec(self):
		self.PutIf()
		if random.randint(1, 6) == 1:
			self.PutElseIf()
		if random.randint(1, 3) == 1:
			self.PutElse()
		return True
	
'''
TODO:
Need apis and weights or something
Should make a seperate program to generate a file, for convenient entry/editing

GetTickCount()
GetCurrentProcessId()
GetCurrentThreadId()
GetCurrentProcess()
GetCurrentThread()
GetModuleHandle(NULL)

Sleep()
'''	
	
class ApiCallControl(ControlType):
	def RandApiNoVar(self):
		apis = ['GetTickCount()', 'GetCurrentProcessId()', 'GetCurrentThreadId()', 'GetCurrentProcess()', 'GetCurrentThread()'
		        , 'GetModuleHandle(NULL)']
		api = random.choice(apis)
		dest = self.variables.Rand(1, globalChance = 0.20)
		self.out.output(dest + ' = (int)' + api + ';')
		self.out.line()
		
	def RandRetlessApiNoVar(self):
		apis = ['Sleep(%u)' % (random.choice([1, 2, 5, 100, 64, 64, 1000]))]
		api = random.choice(apis)
		self.out.output(api + ';')
		self.out.line()
	
	def Exec(self):
		r = random.randint(1, 4)
		if r == 1:
			self.RandRetlessApiNoVar()
		else:
			self.RandApiNoVar()
		return True
	
class StopControl(ControlType):
	def Exec(self):
		return False
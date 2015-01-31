import string
import random

from modWeighted import weightedSample, weightedChoice
from constant import *

class Variables:
	# varCount is total local variables
	# usableVarCount is (local variables + global variables)
	def __init__(self, varCount, globalVars = None):
		if varCount > 26:
			raise Exception('Don\'t you think you\'re being a bit too aggressive?')
		self.varCount = varCount
		lowercase = list(string.ascii_uppercase)
		self.variables = list(map(self._AddNamePrefix, lowercase[0:varCount]))
		
		if globalVars is None:
			self.globalVars = []
		else:
			self.globalVars = globalVars.variables
		
		self.usableVarCount = len(self.globalVars) + varCount
		
		self.constants = Constants()
		self.constants.Initialize()
		
	def _AddNamePrefix(self, letter):
		return letter.lower()
		
	def Rand(self, count = 1, globalChance = 0.0):
		allVars = self.variables + self.globalVars
		
		if globalChance == 0.0:
			allVars = [[var, 1] for var in self.variables]
		else:
			allVars = [[var, 1 - globalChance] for var in self.variables] 
			allVars.extend([[var, globalChance] for var in self.globalVars])
		
		if count > self.usableVarCount:
			raise Exception('Requested more variables than available')
		elif count == 1:
			return weightedChoice(allVars)
		elif count > 1:
			return weightedSample(allVars, count)
		else:
			raise Exception('Invalid argument')
		
	def RandCond(self, count, globalChance = 0):
		if count not in (1, 2):
			raise Exception('RandCond not supported on this count value')
		# get a variable, global, or constant
		result = []
		if random.random() > 0.5:
			result.append(self.Rand(1, globalChance))
		else:
			result.append(str(self.constants.GetConstant()))
		if count == 2:
			result.append(self.Rand(1, globalChance))
			
		return result
		
	def _RandInitialValue(self):
		return self.constants.GetConstant()
	
	def _VarType(self):
		return 'int'
		
	def InitStatement(self, out):
		
		#vars = []
		#for var in self.variables:
			#vars.append('%s = %i' % (var, self._RandInitialValue()))
		#buf += ', '.join(vars) + ';'
		
		#return buf
		
		out.output(self._VarType() + ' ')
		vars = []
		for var in self.variables:
			vars.append('%s = %i' % (var, self._RandInitialValue()))
		out.output(', '.join(vars))
		out.output(';')
		out.line()
		out.line()
		
class VolVariables(Variables):
	def _AddNamePrefix(self, letter):
		return 'autovol' + letter
	
	def _RandInitialValue(self):
		return 0
	
	def _VarType(self):
		return 'volatile int'
	
class ZeroLabelsException(Exception):
	pass
	
class Labels:
	def __init__(self):
		self.Clear()
		
	def Clear(self):
		self.labelCount = 0
		self.__labels = []	
		
	def CreateNew(self):
		result = 'label_' + str(self.labelCount)
		self.__labels.append(result)
		self.labelCount += 1
		return result
	
	def GetRand(self):
		return random.choice(self.__labels)
	
	def ResolveGotos(self, code):
		if len(self.__labels) == 0:
			raise ZeroLabelsException('No labels found')
		else:
			return code.replace('%INSERTLABEL%', self.GetRand())
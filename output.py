class Output:
	def __init__(self):
		self.Clear()
		
	def Clear(self):
		self.outputString = ''
		self.__isLineStart = True
		self.lineCount = 0
		self.nestingLevel = 0			
	
	def __write(self, str):
		self.outputString += str	
		
	def line(self):
		self.__write('\n')
		self.__isLineStart = True
		self.lineCount += 1
		
	def output(self, str):
		# start each line with tabs equal to nesting level		
		if self.__isLineStart:
			for q in range(0, self.nestingLevel):
				self.__write('\t')
			self.__isLineStart = False
			
		self.__write(str)
		
	def incNesting(self):
		self.nestingLevel += 1
		
	def decNesting(self):
		self.nestingLevel -= 1
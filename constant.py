import random

from modWeighted import weightedSample, weightedChoice

class Constants:
    def __init__(self):
        self.choices = {}
            
    def Initialize(self):
        choices = {}
        for q in range(4097):
            choices[q] = 0
        for key in (0, 1):
            choices[key] += 65
        for key in (2, 4, 8, 16):
            choices[key] += 30
        for key in range(32, 64, 128):
            choices[key] += 8            
        for key in range(17):
            choices[key] += 5
        for key in range(2, 100 + 1, 2):
            choices[key] += 2
        for key in (256, 512, 1024, 2048, 4096):
            choices[key] += 2
        for key in range(101):
            choices[key] += 2
            
        choices = {key: choices[key] for key in choices if choices[key] != 0}
        
        self.choices = choices
        self.choiceList = list(self.choices.items())
        
    def GetConstant(self):
        if random.random() > 0.01:
            return weightedChoice(self.choiceList)
        else:
            return random.randint(0, 0x7FFFFFFF)
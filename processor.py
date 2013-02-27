import cache

class Processor:
	
	def __init__(self,name,bus,cacheLineSize,cacheLineCount):
		self.name = name
		self.cache = cache.Cache(cacheLineSize,cacheLineCount,bus,self)
	
	def getName(self):
		return self.name
	
	def executeCommand(self,cmd):
		self.cache.executeCommand(cmd)
		#self.cache.printCache()
	
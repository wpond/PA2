import cache

class Processor:
	
	def __init__(self,name,bus,cacheSize,cacheLines):
		self.name = name
		self.cache = cache.Cache(cacheSize/cacheLines,cacheLines,bus,self)
	
	def getName(self):
		return self.name
	
	def executeCommand(self,cmd):
		self.cache.executeCommand(cmd)
		#self.cache.printCache()
	
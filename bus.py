class Bus:
	
	caches = []
	
	def __init__(self):
		pass
	
	def registerCache(self,cache):
		self.caches.append(cache)
	
	def executeCommand(self,cmd):
		for cache in self.caches:
			cache.snoopCommand(cmd)
	
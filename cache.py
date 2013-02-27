class Cache:
	
	STATES = {
		0: "invalid",
		1: "shared",
		2: "modified",
	}
	
	def __init__(self,lineSize,lineCount,bus,processor):
		self.lineCount = lineCount
		self.lineSize = lineSize
		self.lines = {}
		self.readMisses = 0
		self.writeMisses = 0
		self.invalidations = 0
		self.coherenceMisses = 0
		self.bus = bus
		self.processor = processor
		bus.registerCache(self)
		for i in xrange(lineCount):
			self.lines[i] = {
				"valid": 0, # invalid
				"tag": 0,
				"invalidated": False,
			}
		
	def executeCommand(self,cmd):
		
		if not cmd["processor"] == self.processor.getName():
			return
		
		#print "CMD\t%s\t%s %d" % (self.processor.getName(),cmd["RW"],cmd["address"])
		
		idx = self.getIndex(cmd["address"])
		tag = self.getTag(cmd["address"])
		
		#print "idx = %d\ntag = %d" % (idx,tag)
		
		if self.lines[idx]["tag"] == tag and self.lines[idx]["valid"] == 0 and self.lines[idx]["invalidated"]:
			self.coherenceMisses += 1
		
		if not self.lines[idx]["tag"] == tag or self.lines[idx]["valid"] == 0: # invalid
			#print "block not in cache"
			if cmd["RW"] == "R":
				self.lines[idx]["valid"] = 1
				self.readMisses += 1
			elif cmd["RW"] == "W":
				self.lines[idx]["valid"] = 2
				self.writeMisses += 1
			self.lines[idx]["tag"] = tag
			self.lines[idx]["invalidated"] = False
			self.bus.executeCommand(cmd)
		
		elif self.lines[idx]["valid"] == 1: # shared
			#print "cache shared"
			if cmd["RW"] == "W":
				self.lines[idx]["valid"] = 2
				self.writeMisses += 1
				self.bus.executeCommand(cmd)
		
		#print
		
	def snoopCommand(self,cmd):
		
		if cmd["processor"] == self.processor.getName():
			return
		
		#print "SNP\t%s" % (self.processor.getName())
		
		idx = self.getIndex(cmd["address"])
		tag = self.getTag(cmd["address"])
		
		if not self.lines[idx]["tag"] == tag or self.lines[idx]["valid"] == 0: # invalid
			#print "not in cache"
			pass
		
		elif self.lines[idx]["valid"] == 1: # shared
			#print "shared in cache"
			if cmd["RW"] == "W":
				self.lines[idx]["valid"] = 0
				self.lines[idx]["invalidated"] = True
				self.invalidations += 1
			
		elif self.lines[idx]["valid"] == 2: # modified
			#print "modified in cache"
			if cmd["RW"] == "R":
				self.lines[idx]["valid"] = 1
			elif cmd["RW"] == "W":
				self.lines[idx]["valid"] = 0
				self.lines[idx]["invalidated"] = True
				self.invalidations += 1
		
	def getSize(self):
		return self.lineSize * self.lineCount
	
	# used for testing
	def getOffset(self,addr):
		return addr % self.lineSize
	
	def getIndex(self,addr):
		return (addr / self.lineSize) % self.lineCount
	
	def getTag(self,addr):
		return addr / (self.lineSize * self.lineCount)
	
	def printStats(self):
		print
		print "Processor: %s" % self.processor.getName()
		header = "| %-20s | %-8s |" % ("Statistic","Count")
		print '-' * len(header)
		print header
		print '-' * len(header)
		print "| %-20s | %-8d |" % ("Read Misses",self.readMisses)
		print "| %-20s | %-8d |" % ("Write Misses",self.writeMisses)
		totalMisses = self.writeMisses + self.readMisses
		print "| %-20s | %-8d |" % ("Total Misses",totalMisses)
		print '-' * len(header)
		print "| %-20s | %-8d |" % ("Invalidations",self.invalidations)
		#print "| %-20s | %-8d |" % ("Coherence Misses",self.coherenceMisses)
		print "| %-20s | %-8s |" % ("Coherence Misses","%d%%" % (100*(self.coherenceMisses/float(totalMisses))))
		print '-' * len(header)
		print
		print '-' * len(header)
		print "| %-20s | %-8s |" % ("Line Validity","Count")
		print '-' * len(header)
		
		invalid = 0
		shared = 0
		modified = 0
		for l in self.lines.itervalues():
			if l["valid"] == 0:
				invalid += 1
			elif l["valid"] == 1:
				shared += 1
			elif l["valid"] == 2:
				modified += 1
		
		print "| %-20s | %-8d |" % ("Invalid",invalid)
		print "| %-20s | %-8d |" % ("Shared",shared)
		print "| %-20s | %-8d |" % ("Modified",modified)
		print '-' * len(header)
		print "| %-20s | %-8d |" % ("Total",invalid+shared+modified)
		print '-' * len(header)
		print
	
	def printCache(self):
		print
		print "Processor: %s" % self.processor.getName()
		header = "| %-2s | %-8s | %-3s |" % ("Id","Valid","Tag")
		print '-' * len(header)
		print header
		print '-' * len(header)
		for index,line in self.lines.iteritems():
			print "| %-2.2d | %-8s | %-3d |" % (index,self.STATES[line["valid"]],line["tag"])
		print '-' * len(header)
		print
	
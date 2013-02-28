import processor, cache, bus
import sys

if len(sys.argv) < 3:
	print "Usage: %s <input file> <cache line size> <cache line count>" % sys.argv[0]
	sys.exit(0)

CACHE_LINE_SIZE = int(sys.argv[2])
CACHE_LINE_COUNT = int(sys.argv[3])
INPUT = sys.argv[1]

try:
	f = open(INPUT,"r")
except IOError:
	print "Unable to open: %s" % INPUT
	sys.exit(1)

print
print "%-20s\"%s\"" % ("FILE",INPUT)
print "%-20s%s" % ("CACHE LINE SIZE",CACHE_LINE_SIZE)
print "%-20s%s" % ("CACHE LINE COUNT",CACHE_LINE_COUNT)
print "%-20s%s" % ("CACHE SIZE",CACHE_LINE_SIZE * CACHE_LINE_COUNT)

lines = sum(1 for line in f)
interval = max(lines / 100,1)
print

sys.stdout.write("Analysing\t0%")
f.seek(0)
b = bus.Bus()
p = processor.Processor("P0",b,CACHE_LINE_SIZE,CACHE_LINE_COUNT)
c = p.cache
i = 0
addrs = {}
addrLines = {}
for l in f:
	(proc,rw,addr) = l.split(" ")
	
	addr = int(addr)
	idx = addr - c.getOffset(addr)
	
	if not addr in addrs:
		addrs[addr] = {
			"R": {
				"P0": 0,
				"P1": 0,
				"P2": 0,
				"P3": 0,
			},
			"W": {
				"P0": 0,
				"P1": 0,
				"P2": 0,
				"P3": 0,
			}
		}
	addrs[addr][rw][proc] += 1
	
	if not idx in addrLines:
		addrLines[idx] = {
			"R": {
				"P0": 0,
				"P1": 0,
				"P2": 0,
				"P3": 0,
			},
			"W": {
				"P0": 0,
				"P1": 0,
				"P2": 0,
				"P3": 0,
			}
		}
	addrLines[idx][rw][proc] += 1
	
	i += 1
	if i % interval == 0:
		percent = int(100 * i/float(lines))
		sys.stdout.write("\rAnalysing\t|%s%s| %d%%" % ('=' * (percent/2),' ' * (50 - (percent/2) - 1), percent))
		sys.stdout.flush()

percent = 50
sys.stdout.write("\rAnalysing\t|%s%s| %d%%\n" % ('=' * percent,' ' * (50 - percent - 1), percent*2))
sys.stdout.flush()

privateLineCount = 0 # only accessed by 1 processor
sharedReadOnly = 0 # only read
sharedReadWrite = 0 # read and write, multi processors

accessedBy1Proc = 0
accessedBy2Proc = 0
accessedByMultiProc = 0
for addr in addrs.iterkeys():
	accessFreqs = [
		[addrs[addr]["R"]["P0"], addrs[addr]["W"]["P0"]],
		[addrs[addr]["R"]["P1"], addrs[addr]["W"]["P1"]],
		[addrs[addr]["R"]["P2"], addrs[addr]["W"]["P2"]],
		[addrs[addr]["R"]["P3"], addrs[addr]["W"]["P3"]],
	]
	procAccesses = sum(1 for x in accessFreqs if x[0]+x[1] > 0)
	if procAccesses == 1:
		accessedBy1Proc += 1
	elif procAccesses == 2:
		accessedBy2Proc += 1
	elif procAccesses > 2:
		accessedByMultiProc += 1

for addr in addrLines.iterkeys():
	accessFreqs = [
		[addrLines[addr]["R"]["P0"], addrLines[addr]["W"]["P0"]],
		[addrLines[addr]["R"]["P1"], addrLines[addr]["W"]["P1"]],
		[addrLines[addr]["R"]["P2"], addrLines[addr]["W"]["P2"]],
		[addrLines[addr]["R"]["P3"], addrLines[addr]["W"]["P3"]],
	]
	procAccesses = sum(1 for x in accessFreqs if x[0]+x[1] > 0)
	readCount = sum(x[0] for x in accessFreqs)
	writeCount = sum(x[1] for x in accessFreqs)
	if procAccesses == 1:
		privateLineCount += 1
	if procAccesses > 1 and readCount > 0 and writeCount == 0:
		sharedReadOnly += 1
	if procAccesses > 1 and readCount > 0 and writeCount > 0:
		sharedReadWrite += 1

header = "| %-32s |" % ("Memory Accesses")
print
print '-' * len(header)
print header
print '=' * len(header)
total = float(max(1,len(addrLines)))
print "| %-20s | %8.4f%% |" % ("Private Lines",privateLineCount * 100 / total)
print "| %-20s | %8.4f%% |" % ("Shared Read Only",sharedReadOnly * 100 / total)
print "| %-20s | %8.4f%% |" % ("Shared Read Write",sharedReadWrite * 100 / total)
print '-' * len(header)
total = float(len(addrs))
print "| %-20s | %8.4f%% |" % ("Accessed by 1",accessedBy1Proc * 100 / total)
print "| %-20s | %8.4f%% |" % ("Accessed by 2",accessedBy2Proc * 100 / total)
print "| %-20s | %8.4f%% |" % ("Accessed by >2",accessedByMultiProc * 100 / total)
print '-' * len(header)
print "| %-20s | %-9d |" % ("Unique Addresses",len(addrs))
print "| %-20s | %-9d |" % ("Unique Lines",len(addrLines))
print '-' * len(header)
print

bus = bus.Bus()
processors = []
for i in xrange(4):
	processors.append(processor.Processor("P%d" % i,bus,CACHE_LINE_SIZE,CACHE_LINE_COUNT))

sys.stdout.flush()
sys.stdout.write("Processing\t0%")
i = 0
f.seek(0)
for l in f:
	(processor,rw,addr) = l.split(" ")
	cmd = {
		"processor":processor,
		"RW": rw,
		"address": int(addr)
	}
	for p in processors:
		if p.getName() == processor:
			p.executeCommand(cmd)
	i += 1
	if i % interval == 0:
		percent = int(100 * i/float(lines))
		sys.stdout.write("\rProcessing\t|%s%s| %d%%" % ('=' * (percent/2),' ' * (50 - (percent/2) - 1), percent))
		sys.stdout.flush()

percent = 50
sys.stdout.write("\rProcessing\t|%s%s| %d%%\n" % ('=' * percent,' ' * (50 - percent - 1), percent*2))
sys.stdout.flush()



for p in processors:
	p.cache.printStats()
	#p.cache.printCache()

f.close()

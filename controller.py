import processor, cache, bus
import sys

if len(sys.argv) < 3:
	print "Usage: %s <input file> <cache line size> <cache line count>" % sys.argv[0]
	sys.exit(0)

CACHE_LINE_SIZE = int(sys.argv[2])
CACHE_LINE_COUNT = int(sys.argv[3])
INPUT = sys.argv[1]

bus = bus.Bus()
processors = []
for i in xrange(4):
	processors.append(processor.Processor("P%d" % i,bus,CACHE_LINE_SIZE,CACHE_LINE_COUNT))

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
interval = lines / 100
print

sys.stdout.write("Analysing\t0%")
f.seek(0)
cmds = {}
for l in f:
	(processor,rw,addr) = l.split(" ")
	
	addr = int(addr)
	
	if not addr in cmds:
		cmds[addr] = {
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
	cmds[addr][rw][processor] += 1
	
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
accessedBy2Proc = 0
accessedByMultiProc = 0
for addr in cmds.iterkeys():
	accessFreqs = [
		[cmds[addr]["R"]["P0"], cmds[addr]["W"]["P0"]],
		[cmds[addr]["R"]["P1"], cmds[addr]["W"]["P1"]],
		[cmds[addr]["R"]["P2"], cmds[addr]["W"]["P2"]],
		[cmds[addr]["R"]["P3"], cmds[addr]["W"]["P3"]],
	]
	procAccesses = sum(1 for x in accessFreqs if x[0]+x[1] > 0)
	if procAccesses == 1:
		privateLineCount += 1
	elif procAccesses == 2:
		accessedBy2Proc += 1
	elif procAccesses > 2:
		accessedByMultiProc += 1
	
	readCount = sum(x[0] for x in accessFreqs)
	writeCount = sum(x[1] for x in accessFreqs)
	if procAccesses > 1 and readCount > 0 and writeCount == 0:
		sharedReadOnly += 1
	if procAccesses > 1 and readCount > 0 and writeCount > 0:
		sharedReadWrite += 1

header = "| %-26s |" % ("Memory Accesses")
print
print '-' * len(header)
print header
print '-' * len(header)
total = float(len(cmds))
print "| %-20s | %2d%% |" % ("Private Lines",privateLineCount * 100 / total)
print "| %-20s | %2d%% |" % ("Shared Read Only",sharedReadOnly * 100 / total)
print "| %-20s | %2d%% |" % ("Shared Read Write",sharedReadWrite * 100 / total)
print "| %-20s | %2d%% |" % ("Accessed by 2",accessedBy2Proc * 100 / total)
print "| %-20s | %2d%% |" % ("Accessed by >2",accessedByMultiProc * 100 / total)
print '-' * len(header)
print

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

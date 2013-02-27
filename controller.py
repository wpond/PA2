import processor, cache, bus
import sys

if len(sys.argv) < 3:
	print "Usage: %s <input file> <cache line size> <cache line count>" % sys.argv[0]
	sys.exit(0)

CACHE_SIZE = int(sys.argv[2]) * int(sys.argv[3])
CACHE_LINES = int(sys.argv[3])
INPUT = sys.argv[1]

bus = bus.Bus()
processors = []
for i in xrange(4):
	processors.append(processor.Processor("P%d" % i,bus,CACHE_SIZE,CACHE_LINES))

f = open(INPUT,"r")

lines = sum(1 for line in f)
i = 0
sys.stdout.write("Processing: 0%")
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
	if i % 1000 == 0:
		percent = int(50 * i/float(lines))
		sys.stdout.write("\rProcessing: |%s%s| %d%%" % ('=' * percent,' ' * (50 - percent - 1), percent*2))
		sys.stdout.flush()

sys.stdout.write("\rProcessing: complete%s\n" % (' ' * 50))

for p in processors:
	p.cache.printStats()
	#p.cache.printCache()

f.close()

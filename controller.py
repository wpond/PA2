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
interval = lines / 100
print
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
	if i % interval == 0:
		percent = int(100 * i/float(lines))
		sys.stdout.write("\rProcessing: |%s%s| %d%%" % ('=' * (percent/2),' ' * (50 - (percent/2) - 1), percent))
		sys.stdout.flush()

percent = 50
sys.stdout.write("\rProcessing: |%s%s| %d%%\n" % ('=' * percent,' ' * (50 - percent - 1), percent*2))
sys.stdout.flush()

for p in processors:
	p.cache.printStats()
	#p.cache.printCache()

f.close()

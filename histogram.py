import sys, re, csv, math
from collections import defaultdict

def openFile(filename):
	return csv.reader(open(filename, "r"),delimiter='\t')



tsv_file = openFile(sys.argv[1])
column = int(sys.argv[2])
occurences = defaultdict(int)

for row in tsv_file:
	key = row[column]
	occurences[key] += 1

n = sum(occurences.values())
entropy = 0.0
for key in occurences:
    p = 1.0 * occurences[key] / n
    entropy -= p * math.log(p)

print "entropy:", entropy

for key in occurences:
	#print str(occurences[key]) + "," + key + "," + str(len(key))
    pass



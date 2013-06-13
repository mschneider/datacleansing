import sys, re
import csv
from collections import defaultdict

def openFile(filename):
	return csv.reader(open(filename, "r"),delimiter='\t')



tsv_file = openFile(sys.argv[1])
column = int(sys.argv[2])
occurences = defaultdict(int)

for row in tsv_file:
	key = row[column]
	occurences[key] += 1

for key in occurences:
	print str(occurences[key]) + "," + key




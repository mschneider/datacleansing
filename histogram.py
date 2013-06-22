import sys, re, csv, math
from collections import defaultdict

def openFile(filename):
	return csv.reader(open(filename, "r"),delimiter='\t')




for column in range(15)[1:]:
	tsv_file = openFile(sys.argv[1])
	occurences = defaultdict(int)
	for row in tsv_file:
		key = row[column]
		occurences[key] += 1

	distinct_values = len(occurences.keys())
	print column, "distinct:", distinct_values

	entropy = 0.0
	n = sum(occurences.values())
	for key in occurences:
		p = 1.0 * occurences[key] / n
		entropy -= p * math.log(p)
	print column, "entropy:", entropy



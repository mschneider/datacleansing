import sys, re
import csv

def open_tsv(filename):
	return csv.reader(open(filename, "r"), delimiter='\t')

class Duplicates:
	def __init__(self, power_set = set()):
		self.power_set = power_set

	def add(self, file_contents):
		for row in file_contents:
			self.power_set.add(frozenset(row))

	def transitive_closure(self):
		num_unions = 0
		new_power_set = set()
		for s1 in self.power_set:
			for s2 in self.power_set:
				if s1 != s2 and not s1.isdisjoint(s2):
					s1 = s1 | s2
					num_unions += 1
			new_power_set.add(s1)
		self.power_set = (new_power_set)
		print num_unions
		if num_unions == 0:
			return self
		else:
			return self.transitive_closure()

	def set(self, row, column):
		if not row in self.matrix:
			self.matrix[row] = set()
		self.matrix[row].add(column)

duplicates = Duplicates()
for file_name in sys.argv[1:]:
	duplicates.add(open_tsv(file_name))
result = duplicates.transitive_closure()
for s in result.power_set:
	print "\t".join(s)

import sys, re
import csv

def open_tsv(filename):
	return csv.reader(open(filename, "r"), delimiter='\t')

class DuplicateMatrix:
	def __init__(self, file):
		self.maximum = 0
		self.minimum = 9999999
		self.matrix = {}
		if file != None:
			for row in file:
				self.add(*row)

	def add(self, *items):
		items = map(int, list(items))
		self.maximum = max(list(items) + [self.maximum])
		self.minimum = min(list(items) + [self.minimum])
		for item in items:
			for other in items:
				if item < other:
					self.set(item, other)

	def set(self, row, column):
		if not row in self.matrix:
			self.matrix[row] = set()
		self.matrix[row].add(column)

	def count(self):
		result = 0
		for row, columns in self.matrix.items():
			result += len(columns)
		return result

	# other - self
	def difference_to(self, other):
		result = DuplicateMatrix(None)
		for row in other.matrix.keys():
			for column in other.matrix[row]:
				if not row in self.matrix or not column in self.matrix[row]:
					result.set(row, column)
		return result

	def intersect(self, other):
		result = DuplicateMatrix(None)
		for row in other.matrix.keys():
			for column in other.matrix[row]:
				if row in self.matrix and column in self.matrix[row]:
					result.set(row, column)
		return result


result = DuplicateMatrix(open_tsv(sys.argv[1]))
print "result | min:", result.minimum, " max:", result.maximum
gold_standard = DuplicateMatrix(open_tsv(sys.argv[2]))
print "gold_standard | min:", gold_standard.minimum, " max:", gold_standard.maximum
false_positives = gold_standard.difference_to(result)
false_negatives = result.difference_to(gold_standard)
true_positives = result.intersect(gold_standard)
print "fp:", false_positives.count()
print "fn:", false_negatives.count()
print "tp:", true_positives.count()
precision = true_positives.count() * 1.0 / ( true_positives.count() + false_positives.count())
recall = true_positives.count() * 1.0 / ( true_positives.count() + false_negatives.count())
print "precision:", precision
print "recall:", recall
print "f-measure:", 2 * precision * recall / ( precision + recall)

#for row in result.matrix.keys():
	#for index, column1 in enumerate(result.matrix[row]):
		#for column2 in result.matrix[row][index+1:]:
			#if column1 in result.matrix.keys() and column2 in result.matrix[column1]:
				#print "trans:", row, column1, column2
			#elif column2 in result.matrix.keys() and column1 in result.matrix[column2]:
				#print "trans':", row, column1, column2
			#else:
				#print "intrans:", row, column1, column2

exit()
print "false_positives:"
for row in false_positives.matrix.keys():
	for column in false_positives.matrix[row]:
		print str(row)+","+str(column)



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
			self.matrix[row] = []
		self.matrix[row] += [column]

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
false_positives = gold_standard.difference_to(result).count()
false_negatives = result.difference_to(gold_standard).count()
true_positives = result.intersect(gold_standard).count()
print "fp:", false_positives, "fn:", false_negatives, "tp:", true_positives
precision = true_positives * 1.0 / ( true_positives + false_positives)
recall = true_positives * 1.0 / ( true_positives + false_negatives)
print "precision:", precision, "recall:", recall
print "f-measure:", 2 * precision * recall / ( precision + recall)

print "true positives:"
for row in result.intersect(gold_standard).matrix.keys():
	for column in result.intersect(gold_standard).matrix[row]:
		print row, "<->", column



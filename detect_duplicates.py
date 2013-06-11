import sys, re
import csv
import jellyfish

def open_tsv(filename):
	return csv.reader(open(filename, "r"), delimiter='\t')

def write_tsv(filename, result):
	output = open(filename, "w")
	for item in result:
		output.write("\t".join(map(str,item))+"\n")
	output.close()

class Row:
	def __init__(self, fields):
		self.id = fields[0]
		self.culture = fields[1]
		self.sex = fields[2]
		self.age = fields[3]
		self.birthday = fields[4]
		self.title = fields[5]
		self.name = fields[6]
		self.surname = fields[7]
		self.state = fields[8]
		self.suburb = fields[9]
		self.post = fields[10]
		self.street = fields[11]
		self.address1 = fields[12]
		self.address2 = fields[13]
		self.phone = fields[14]

	def __str__(self):
		return "id:" + self.id + "\tc:" + self.culture + "\ts:" + self.sex + "\ta:" + self.age + \
			"\tbd:" + self.birthday + "\tt:" + self.title + "\tn:" + self.name + "\tsn:" + self.surname + \
			"\tst:" + self.state + "\tsb:" + self.suburb + "\tp:" + self.post + "\ts:" + self.street + \
			"\ta1:" + self.address1 + "\ta2" + self.address2 + "\tph" + self.phone

	def compareTo(self, other):
		return \
			rateMatchOrNone(self.culture, other.culture) + \
			rateMatchOrNone(self.sex, other.sex) + \
			rateMatchOrNone(self.age, other.age) + \
			rateEdit(self.birthday, other.birthday) + \
			rateMatchOrNone(self.title, other.title) + \
			rateEdit(self.name, other.name) + \
			rateEdit(self.surname, other.surname) + \
			rateMatchOrNone(self.state, other.state) + \
			rateEdit(self.suburb, other.suburb) + \
			rateEdit(self.post, other.post) + \
			rateMatchOrNone(self.street, other.street) + \
			rateEdit(self.address1, other.address1) + \
			rateEdit(self.address2, other.address2) + \
			rateEdit(self.phone, other.phone)

def rateMatchOrNone(a, b):
	ignored = [None, "", "_", " "]
	a_ignored = a in ignored
	b_ignored = b in ignored
	if a_ignored and b_ignored:
		return 1.0
	elif a_ignored or b_ignored:
		return 0.5
	elif a == b:
		return 1.0
	else:
		return 0.0

def rateEdit(a, b):
	ignored = [None, "", "_", " "]
	a_ignored = a in ignored
	b_ignored = b in ignored
	if a_ignored and b_ignored:
		return 1.0
	elif a_ignored or b_ignored:
		return 0.5
	lev = jellyfish.levenshtein_distance(a,b)
	return max(1.0 - lev * 0.4, 0.0)

input = sys.argv[1]
threshold = float(sys.argv[2])
output = sys.argv[3]

rows = []
for index, r in enumerate(open_tsv(input)):
	rows.append(Row(r))
	if index > 99999:
		break

results = []
for index, row in enumerate(rows):
	if index % 1000 == 0:
		print "" + output + ">", index
	for other in rows[index+1:]:
		if row.compareTo(other) > threshold:
			print "found:", len(results)
			print str(row)
			print str(other)
			results += [[row.id, other.id]]
			if len(results) % 10 == 0:
				write_tsv(ouptut, results)

write_tsv(ouptut, results)




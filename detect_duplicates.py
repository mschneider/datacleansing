import sys, re
import csv
import jellyfish
import ngram
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="Name of File that get checked for duplicates")
parser.add_argument("threshold",type=int, help="Threshold value counts as duplicate.")
parser.add_argument("output", help="Name of Outputfile")
parser.add_argument("-si", "--similarity",type=int,help="Select Simmilarity Measure used. 1= Jaro Winkler,2=Hamming Distance,3=Damerau Levenshtein", choices=[1,2,3])
args = parser.parse_args()


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
				rateWhitelisted(self.sex, other.sex, ['m', 'f']) + \
				rateWhitelisted(self.age, other.age, ['20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40','41','42','43','44']) + \
				rateEdit(repairstring(self.birthday,8),repairstring(other.birthday,8)) + \
				rateMatchOrNone(self.title, other.title) + \
				rateEdit(self.name, other.name) + \
				rateEdit(self.surname, other.surname) + \
				rateMatchOrNone(self.state, other.state) + \
				rateEdit(self.suburb, other.suburb) + \
				rateEdit(repairstring(self.post,4),repairstring(other.post,4)) + \
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

def rateWhitelisted(a, b, whitelist):
	if a in whitelist and b in whitelist:
		if a.strip() == b.strip():
			return 1.0
		else:
			return 0.0
	else:
		return 0.5
		
def repairstring(a,deflen):
		a=a.strip()
		if len(a) - a.count(' ')== deflen:
			a = a.replace(" ","")
			return a
		else:
			return a
			
		
def rateDate(a, b):
	valid_date = re.compile('^19[0-9]{6}$')
	a_is_valid = valid_date.match(a)
	b_is_valid = valid_date.match(b)
	if a_is_valid and b_is_valid:
		if a == b:
			return 1.0
		else:
			return 0.0
	else:
		return distance(a, b)

#Example Code for NGRAMM
#ng=ngram.NGram(pad_len=1,N=2)
#list(ng.ngrams(ng.pad("Tester"))
#>> ['$T', 'Te', 'es', 'st', 'te', 'er', 'r$']

def distance(a,b):
	similaritycalc = {
	        	1: lambda a,b:  1.0 - float(jellyfish.jaro_winkler(a, b)) / max(len(a), len(b)),
				2: lambda a,b:  1.0 - float(jellyfish.hamming_distance(a, b)) / max(len(a), len(b)),
				3:lambda a,b:  1.0 - float(jellyfish.damerau_levenshtein_distance(a, b)) / max(len(a), len(b)),
				None:lambda a,b:  1.0 - float(jellyfish.damerau_levenshtein_distance(a, b)) / max(len(a), len(b))
				}
		
	return similaritycalc[args.similarity](a,b)

def rateEdit(a, b):
	ignored = [None, "", "_", " "]
	a_ignored = a in ignored
	b_ignored = b in ignored
	if a_ignored and b_ignored:
		return 1.0
	elif a_ignored or b_ignored:
		return 0.5
	return distance(a,b)


input = args.filename

rows = []
for index, r in enumerate(open_tsv(input)):
	rows.append(Row(r))
	if index > 99999:
		break

threshold = float(args.threshold)
output = args.output
results = []
rows.sort(key = lambda row: row.phone)
for index, row in enumerate(rows):
	if index % 1000 == 0:
		print "" + output + ">", index
	for other in rows[index+1:index+11]:
		if row.compareTo(other) > threshold:
			print "found:", len(results)
			print str(row)
			print str(other)
			results += [[row.id, other.id]]
			if len(results) % 1000 == 0:
				write_tsv(output, results)
write_tsv(output, results)







import sys, re
import csv
import jellyfish
import ngram
import argparse
import operator
from collections import defaultdict


parser = argparse.ArgumentParser()
parser.add_argument("filename", help="Name of File that get checked for duplicates")
parser.add_argument("threshold",type=float, help="Threshold value counts as duplicate.")
parser.add_argument("output", help="Name of Outputfile")
parser.add_argument("-s", "--similarity",type=str,help="Select Simmilarity Measure used.",default="dice" , choices=["jaro_winckler","hamming_distance","damreau_levenshtein","dice", "jaccard"])
parser.add_argument("-m","--mean",type=str, help="Select Mean Calculation", default="arithemtic_weighted_mean",choices=["arithmetic_mean","arithemtic_weighted_mean","geometric_mean","geometric_weighted_mean"])
parser.add_argument("-d","--diff",type=str, help="diff 2 rows")
parser.add_argument("-w","--window",type=str, help="sliding window")
parser.add_argument("-c","--column",type=int, help="sort column")
args = parser.parse_args()

def arithmeticMean(similarities, weights):
	return float(sum(similarities)) / len(similarities)

def arithmeticWeightedMean(similarities, weights):
	weightedSum = 0.0
	for x, y in zip(similarities, weights):
		weightedSum += x * y
	return weightedSum / sum(weights)

def geometricMean(similarities, weights):
	return reduce(operator.mul, similarities) ** (1.0 / len(similarities))

def geometricWeightedMean(similarities, weights):
	weightedProduct = 0.0
	for x,y in zip(similarities, weights):
		weightedProduct *= x ** y
	return weightedProduct ** (1.0 / sum(weights))

def dice(a,b):
	ng=ngram.NGram(pad_len=1,N=2)
	a = set(ng.ngrams(ng.pad(a)))
	b = set(ng.ngrams(ng.pad(b)))
	overlap = len(a & b)
	return overlap * 2.0/(len(a) + len(b))

def jaccard(a, b):
	ng=ngram.NGram(pad_len=1,N=2)
	a = set(ng.ngrams(ng.pad(a)))
	b = set(ng.ngrams(ng.pad(b)))
	return len(a & b) * 1.0 / len(a | b)


similarity = {
	"jaro_winckler": lambda a,b: jellyfish.jaro_winkler(a, b),
	"hamming_distance": lambda a,b:  1.0 - float(jellyfish.hamming_distance(a, b)) / max(len(a), len(b)),
	"damreau_levenshtein":lambda a,b:  1.0 - float(jellyfish.damerau_levenshtein_distance(a, b)) / max(len(a), len(b)),
	"dice":dice,
	"jaccard":jaccard
}[args.similarity]

mean = {
	"arithmetic_mean":arithmeticMean,
	"arithemtic_weighted_mean":arithmeticWeightedMean,
	"geometric_mean":geometricMean,
	"geometric_weighted_mean": geometricWeightedMean
}[args.mean]

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
		similarities=[rateMatchOrNone(self.culture, other.culture), \
			rateWhitelisted(self.sex, other.sex, ['m', 'f']), \
			rateWhitelisted(self.age, other.age, ['20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38']), \
			rateEdit(self.birthday,other.birthday), \
			rateMatchOrNone(self.title, other.title), \
			max(rateEdit(self.name, other.name), rateEdit(self.name, other.surname)), \
			max(rateEdit(self.surname, other.surname), rateEdit(self.surname, other.name)), \
			rateMatchOrNone(self.state, other.state) , \
			rateEdit(self.suburb, other.suburb), \
			rateEdit(self.post,other.post), \
			rateMatchOrNone(self.street, other.street), \
			rateEdit(self.address1, other.address1), \
			rateEdit(self.address2, other.address2), \
			rateEdit(self.phone, other.phone)]
		# calculated through entropy
		weights = [
				2.71362190507,
				0.991606467856,
				3.36756458423,
				9.32860330905,
				1.42942219466,
				6.93610674013,
				9.01046604867,
				2.14344653528,
				9.3628288518,
				7.3685052645,
				5.11222524931,
				8.5275890737,
				4.44927477503,
				13.182882853]

		return mean(similarities,weights)


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
		if a==b:
			return 1.0
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
		return similarity(a, b)

#Example Code for NGRAMM
#ng=ngram.NGram(pad_len=1,N=2)
#list(ng.ngrams(ng.pad("Tester"))
#>> ['$T', 'Te', 'es', 'st', 'te', 'er', 'r$']

def rateEdit(a, b):
	ignored = [None, "", "_", " "]
	a_ignored = a in ignored
	b_ignored = b in ignored
	if a_ignored and b_ignored:
		return 1.0
	elif a_ignored or b_ignored:
		return 0.5
	return similarity(a,b)


input = args.filename
rows = []

if args.diff != None:
	a, b = map(int, args.diff.split(','))
	for index, r in enumerate(open_tsv(input)):
		if index == a or index == b:
			rows.append(Row(r))
			if len(rows) > 1:
				break

	print rows[0]
	print rows[1]
	print rows[0].compareTo(rows[1])
	exit()

if args.window != None:
	column, id, other_id = args.window.split(',')
	ng=ngram.NGram(pad_len=1,N=8)
	stopwords = set() # set(ng.ngrams("street")) | set(ng.ngrams("circuit"))
	ngrams_to_rows = defaultdict(list)
	value_in_column = eval("lambda r: r."+column)
	for index, r in enumerate(open_tsv(input)):
		row = Row(r)
		rows.append(row)
		for token in set(ng.ngrams(value_in_column(row))) - stopwords:
			ngrams_to_rows[token].append(row)
	candidates = set()
	for token in set(ng.ngrams(value_in_column(rows[int(id)]))) - stopwords:
		print token
		candidates |= set(ngrams_to_rows[token])
	print len(candidates)
	for candidate in candidates:
		if candidate.id == other_id:
			print other_id, "included"

for index, r in enumerate(open_tsv(input)):
	rows.append(Row(r))
	#if index >= 100000:
		#break


threshold = float(args.threshold)
output = args.output
results = []
columns = [
	lambda r: r.phone.replace(" ", ""),
	lambda r: r.suburb.replace(" ", ""),
	lambda r: r.birthday.replace(" ",""),
	lambda r: r.address1.replace(" ",""),
	lambda r: r.address2.replace(" ",""),
	lambda r: r.surname.replace(" ",""),
	lambda r: r.name.replace(" ",""),
	lambda r: r.post.replace(" ","") + r.address1.replace(" ",""),
	lambda r: r.culture.replace(" ","") + r.name.replace(" ",""),
	lambda r: r.culture.replace(" ","") + r.surname.replace(" ","")]
column = columns[args.column]
rows.sort(key = column)
for index, row in enumerate(rows):
    if index % 1000 == 0:
        print "" + output + ">", index
    for other in rows[index+1:index+11]:
        if row.compareTo(other) > threshold:
            results += [[row.id, other.id]]
write_tsv(output, results)







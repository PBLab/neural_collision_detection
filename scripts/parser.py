#!/usr/bin/python

import os, sys

class ResultsParser:
	def __init__(self, lines):
		#with open(fname, "rb") as f:
			#self.lines = f.readlines()
		self.lines = lines
		self.idx = 0
		self.total_len = len(lines)

	def __len__(self):
		return self.total_len

	def __iter__(self):
		self.idx = 0
		return self

	def next(self):
		if self.idx >= self.total_len:
			raise StopIteration
		self.idx += 1
		return self.lines[self.idx - 1]

	def where(self, f):
		lines = []
		for l in self.lines:
			if f(l):
				lines.append(l)
		return ResultsParser(lines)
		


def main(argv):
	if len(argv) < 2:
		print "Usage: %s <input file>" % argv[0]
		return 1
	
	input_filename = argv[1]

	parser = ResultsParser(open(input_filename).readlines())
	print len(parser)

	COL_COLLISIONS = 5
	print "\n".join(parser.where(lambda x: x.startswith("agg_distance_0,")).\
						where(lambda x : len(x.split(",")[COL_COLLISIONS].split("|")) < 6))
	#print "\n".join(parser.where(lambda x: x.startswith("agg_distance_0,")).where(lambda x : len(x.split(",")[COL_COLLISIONS].split("|")) <= 10).lines)
	
if __name__ == "__main__":
	main(sys.argv)

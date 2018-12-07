#!/state/partition1/apps/python/anaconda2/bin/python

import sys

def get_collisions_cnt(l):
	return int(l.split(",")[7])

def main(argv):
	if len(argv) != 4:
		print "Usage: %s <input file> <output file> <results count>" % argv[0]
		return 1
	
	input_fname = argv[1]
	output_fname = argv[2]
	results_count = int(argv[3])

	with open(input_fname, "r") as f:
		lines = f.read().split("\n")
		if lines[-1] == "":
			lines = lines[:-1]
	
	print "Total lines: %i" % len(lines)

	sorted_lines = sorted(lines, key=get_collisions_cnt)
	res = sorted_lines[:results_count]

	print "Leaving %i lines" % len(res)

	with open(output_fname, "w") as f:
		for r in res:
			f.write(r + "\n")

if __name__ == "__main__":
	main(sys.argv)

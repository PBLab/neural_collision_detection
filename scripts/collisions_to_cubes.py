#!/usr/bin/python
import os, sys

def main(argv):
	if len(argv) < 3:
		print "Usage: %s <input file> <output dir>" % argv[0]
		return 1
	
	input_filename = argv[1]
	output_dir = argv[2]
	if len(argv) > 3:
		r = float(argv[3])

	with open(input_filename, "r") as f:
		lines = f.read().split("\n")

	lines = [l for l in lines if len(l) > 1]
	lines = list(set(lines))
	output_idx = 0
	for l in lines:
		output = os.path.join(output_dir, "collision_{0}.obj".format(output_idx))
		os.system("python ~/cg/tests/create_cube.py {output} {r} {l}".format(**locals()))
		output_idx += 1


if __name__ == "__main__":
	main(sys.argv)

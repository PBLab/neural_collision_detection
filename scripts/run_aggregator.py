#!/usr/bin/python

import os, sys, re
from aggregator import aggregate

def get_file_size(fname):
	return os.path.getsize(fname)

def get_zero_files(root):
	l = []
	for dirpath, dirnames, filenames in os.walk(root):
		for f in filenames:
			full_filename = os.path.join(dirpath, f)
			if get_file_size(full_filename) == 0:
				l.append(full_filename)
	return l
	
def create_cmd(out_dir, neuron_name, location, rotation):
	l = ",".join(location)
	r = ",".join(rotation)
	out_file = "{0}/out_{1}_{2}_{3}.txt".format(out_dir, neuron_name, l, r).replace(",", "_")
	neuron_name = neuron_name.replace(".obj", "_balls.csv")
	return "./aggregator.py ../../vascular/vascular_balls.csv ../../neurons/{0} {2} {3} {1}".format(neuron_name, out_file, l, r)

def main(argv):
	if len(argv) < 3:
		print "Usage: %s <base dir> <out dir>" % argv[0]
		return 1

	base_dir = argv[1]
	out_dir = argv[2]

	os.system("mkdir {0}".format(out_dir))

	re_exp = "/(\w+.obj)_([0-9-]+)_([0-9-]+)_([0-9-]+)__([0-9-]+)_([0-9-]+)_([0-9-]+)_collision.txt"
	zero_files = get_zero_files(base_dir)
	total_files = len(zero_files)
	print "Running over {0} files".format(total_files)

	cnt = 0
	for fname in zero_files:
		print "\n=== File #{0} / {1} ===\n".format(cnt, total_files)
		m = re.search(re_exp, fname)

		neuron_name = m.group(1)
		location = [m.group(2), m.group(3), m.group(4)]
		rotation = [m.group(5), m.group(6), m.group(7)]

		l = ",".join(location)
		r = ",".join(rotation)

		location = [int(x) for x in location]
		rotation = [int(x) for x in rotation]

		out_file = "{0}/out_{1}_{2}_{3}.txt".format(out_dir, neuron_name, l, r).replace(",", "_")
		neuron_name = neuron_name.replace(".obj", "_balls.csv")
		neuron_fname = "../../neurons/" + neuron_name
		vascular_fname = "../../vascular/vascular_balls.csv"

		aggregate(vascular_fname, neuron_fname, location, rotation, out_file)

		cnt += 1
		#cmd = create_cmd(out_dir, neuron_name, location, rotation)
		#print cmd
		#os.system(cmd)


if __name__ == "__main__":
	sys.exit(main(sys.argv))

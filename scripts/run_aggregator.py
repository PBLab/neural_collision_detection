#!/usr/bin/python

import os, sys, re, threading
from aggregator import aggregate, get_vascular

def get_file_size(fname):
	return os.path.getsize(fname)

def get_number_of_lines(fname):
	num_lines = sum(1 for line in open(fname))
	return num_lines

def get_small_files(root, max_line_count):
	l = []
	for dirpath, dirnames, filenames in os.walk(root):
		for f in filenames:
			if "collision.txt" not in f:
				continue
			full_filename = os.path.join(dirpath, f)
			if get_number_of_lines(full_filename) <= max_line_count:
				l.append(full_filename)
	return l
	

def thread_main(fnames, out_dir, threshold_distance, vascular):
	for fname in fnames:
		re_exp = "/(\w+.obj)_([0-9-]+)_([0-9-]+)_([0-9-]+)__([0-9-]+)_([0-9-]+)_([0-9-]+)_collision.txt"
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

		aggregate(vascular_fname, neuron_fname, location, rotation, out_file, threshold_distance, vascular)


def main(argv):
	if len(argv) < 4:
		print "Usage: %s <base dir> <max collisions> <threshold distance> <out dir>" % argv[0]
		return 1

	base_dir = argv[1]
	number_of_lines = int(argv[2])
	threshold_distance = int(argv[3])
	out_dir = argv[4]

	os.system("mkdir {0}".format(out_dir))

	small_files = get_small_files(base_dir, number_of_lines)
	total_files = len(small_files)
	print "Running over {0} files".format(total_files)

	thread_count = 24
	#thread_count = 24
	fnames_per_thread = 1.0 * len(small_files) / thread_count
	threads = []
	last_idx = 0
	vascular_fname = "../../vascular/vascular_balls.csv"
	vascular = get_vascular(vascular_fname)
	for i in xrange(thread_count):
		next_idx = int(fnames_per_thread * (i + 1))
		if i == thread_count - 1:
			next_idx = len(small_files)

		params = (small_files[last_idx : next_idx], out_dir, threshold_distance, vascular)
		print len(params[0])

		t = threading.Thread(target=thread_main, args = params)
		threads.append(t)
		t.start()
		last_idx = next_idx

	for i in xrange(thread_count):
		threads[i].join()

if __name__ == "__main__":
	sys.exit(main(sys.argv))

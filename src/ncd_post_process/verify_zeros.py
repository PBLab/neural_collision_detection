#!/usr/bin/python

import os, sys, re

def get_file_size(fname):
	return os.path.getsize(fname)


def get_zero_files(root):
	l = []
	for dirpath, dirnames, filenames in os.walk("."):
		for f in filenames:
			full_filename = os.path.join(dirpath, f)
			if get_file_size(full_filename) == 0:
				l.append(full_filename)
	return l
	
def create_cmd(neuron_name, location, rotation):
	l = ",".join(location)
	r = ",".join(rotation)
	out_dir = "verify_zeros/out_{0}_{1}_{2}".format(neuron_name, l, r).replace(",", "_")
	return "./ncd -m verify -V ../vascular/vascular.0.999.obj -N ../neurons/{0} -o {1} -l {2} -r {3}".format(neuron_name, out_dir, l, r)

def main(argv):
	if len(argv) < 2:
		print("Usage: %s <base dir>" % argv[0])
		return 1

	base_dir = argv[1]

	#./extended_out9/AP120510_s1c1.obj_505_502_592__4_-1_32_collision.txt
	#re_exp = "extended_out[0-9-]*/(\w+.obj)_([0-9-]+)_([0-9-]+)_([0-9-]+)__([0-9-]+)_([0-9-]+)_([0-9-]+)_collision.txt"
	re_exp = "/(\w+.obj)_([0-9-]+)_([0-9-]+)_([0-9-]+)__([0-9-]+)_([0-9-]+)_([0-9-]+)_collision.txt"
	zero_files = get_zero_files(base_dir)
	for fname in zero_files:
		#print fname
		m = re.search(re_exp, fname)
		#print m.group(0)
		neuron_name = m.group(1)
		location = [m.group(2), m.group(3), m.group(4)]
		rotation = [m.group(5), m.group(6), m.group(7)]
		cmd = create_cmd(neuron_name, location, rotation)
		print(cmd)
		os.system(cmd)
	#print "\n".join(get_zero_files("."))
	


if __name__ == "__main__":
	sys.exit(main(sys.argv))

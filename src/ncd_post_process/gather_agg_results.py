#!/usr/bin/python
from __future__ import print_function
import sys, os, re

def get_collision_string(fname):
	res = ""
	for line in open(fname, "r"):
		x, y, z = line.replace("\n","").split(",")
		col = " ".join([x, y, z])
		res += col + "|"
	return res[:-1]


def main(argv):
	if len(argv) != 3:
		print("Usage: %s <input directory> <output file>" % argv[0])
		return 1

	input_dir, output_file = argv[1:3]
	if input_dir.endswith("/"):
		input_dir = input_dir[:-1]

	re_exp = r"(\w+.obj)_([0-9-]+)_([0-9-]+)_([0-9-]+)_([0-9-]+)_([0-9-]+)_([0-9-]+).txt"
	with open(output_file, "a") as out:

		for fname in os.listdir(input_dir):
			m = re.search(re_exp, fname)
			print(m.group(0))
			neuron_name = m.group(1).replace(".obj","").replace("out_","")
			location = [m.group(2), m.group(3), m.group(4)]
			rotation = [m.group(5), m.group(6), m.group(7)]
			#print neuron_name, location, rotation

			run_id = os.path.basename(input_dir)
			neuron_id = neuron_name
			vascular_id = "vascular1"
			neuron_location = "{0} {1} {2}".format(*location)
			neuron_rotation = "{0} {1} {2}".format(*rotation)
			full_fname = os.path.join(input_dir, fname)
			collisions = get_collision_string(full_fname)
			line = "{run_id},{neuron_id},{vascular_id},{neuron_location},{neuron_rotation},{collisions}\n".format(**locals())
			out.write(line)


if __name__ == "__main__":
	main(sys.argv)

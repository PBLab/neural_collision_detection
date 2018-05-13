#!/usr/bin/python
import os, sys

def find_bounding_box(obj):
	min_x = max_x = obj[0][0]
	min_y = max_y = obj[0][1]
	min_z = max_z = obj[0][2]

	for i in xrange(len(obj)):
		x, y, z = obj[i][:3]
		if x < min_x:
			min_x = x
		if x > max_x:
			max_x = x
		if y < min_y:
			min_y = y
		if y > max_y:
			max_y = y
		if z < min_z:
			min_z = z
		if z > max_z:
			max_z = z

	return min_x, max_x, min_y, max_y, min_z, max_z

def handle_obj_file(fname):
	obj = []
	for line in open(fname, "rb"):
		if not line.startswith("v "):
			continue
		point = line.split(" ")[1:4]
		point = [float(x) for x in point]
		obj.append(point)

	return find_bounding_box(obj)

def handle_csv_file(fname):
	obj = []
	for line in open(fname, "rb"):
		point = line.split(",")[:3]
		point = [float(x) for x in point]
		obj.append(point)

	return find_bounding_box(obj)

def main(argv):
	if len(argv) != 2:
		print "Usage: %s <object>" % argv[0]
		return 1

	fname = argv[1]

	if fname.endswith(".obj"):
		bb = handle_obj_file(fname)
	elif fname.endswith(".csv"):
		bb = handle_csv_file(fname)
	else:
		print "Unknown file extension"
		return 1

	print "X: {0}\t-\t{1}".format(bb[0], bb[1])
	print "Y: {0}\t-\t{1}".format(bb[2], bb[3])
	print "Z: {0}\t-\t{1}".format(bb[4], bb[5])

if __name__ == "__main__":
	main(sys.argv)

#!/usr/bin/python
import os, sys

def find_bounding_box(obj):
	min_x = max_x = obj[0][0]
	min_y = max_y = obj[0][1]
	min_z = max_z = obj[0][2]

	for i in xrange(len(obj)):
		x, y, z, r = obj[i]
		#r = 0
		if x-r < min_x:
			min_x = x-r
		if x+r > max_x:
			max_x = x+r
		if y-r < min_y:
			min_y = y-r
		if y+r > max_y:
			max_y = y+r
		if z-r < min_z:
			min_z = z-r
		if z+r > max_z:
			max_z = z+r

	return min_x, max_x, min_y, max_y, min_z, max_z

def get_bb_obj_file(fname):
	obj = []
	for line in open(fname, "rb"):
		if not line.startswith("v "):
			continue
		point = line.split(" ")[1:4]
		point = [float(x) for x in point] + [0]
		obj.append(point)

	return find_bounding_box(obj)

def get_bb_csv_file(fname):
	obj = []
	for line in open(fname, "rb"):
		point = line.split(",")
		point = [float(x) for x in point]
		obj.append(point)

	return find_bounding_box(obj)

def get_bb(fname):
	if fname.endswith(".obj"):
		bb = get_bb_obj_file(fname)
	elif fname.endswith(".csv"):
		bb = get_bb_csv_file(fname)
	else:
		raise Exception("Unknown file extension")
	return bb

def main(argv):
	if len(argv) != 2:
		print "Usage: %s <object>" % argv[0]
		return 1

	fname = argv[1]

	bb = get_bb(fname)

	print "X: {0}\t-\t{1}\t[{2}]".format(bb[0], bb[1], bb[1]-bb[0])
	print "Y: {0}\t-\t{1}\t[{2}]".format(bb[2], bb[3], bb[3]-bb[2])
	print "Z: {0}\t-\t{1}\t[{2}]".format(bb[4], bb[5], bb[5]-bb[4])

if __name__ == "__main__":
	main(sys.argv)

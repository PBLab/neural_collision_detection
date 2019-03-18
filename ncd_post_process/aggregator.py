#!/state/partition1/apps/python/anaconda2/bin/python
from __future__ import print_function
import sys, os
import math
import numpy as np
import time
import bisect

def create_collision_str(collisions):
	res = ""
	for c in collisions:
		x, y, z, _ = [str(a) for a in c]
		col = " ".join([x, y, z])
		res += col + "|"
	return res[:-1]

def read_balls(fname):
	res = []

	for line in open(fname, "r"):
		if len(line) <= 1:
			pass
		x, y, z, r = [float(a) for a in line.split(",")]
		res.append([x, y, z, r])
	return res

def swap_x_y(obj):
	for i in range(len(obj)):
		x, y, z, r = obj[i]
		obj[i] = [y, x, z, r]

def rotate(neuron, rotation):
	x_deg, y_deg, z_deg = rotation
	x_rad = math.radians(x_deg)
	y_rad = math.radians(y_deg)
	z_rad = math.radians(z_deg)

	cos_x = math.cos(x_rad)
	sin_x = math.sin(x_rad)
	cos_y = math.cos(y_rad)
	sin_y = math.sin(y_rad)
	cos_z = math.cos(z_rad)
	sin_z = math.sin(z_rad)

	m_x = [[1, 0, 0],
			[ 0, cos_x, -1*sin_x],
			[0, sin_x, cos_x]]

	m_y = [[cos_y, 0, sin_y],
			[0, 1, 0],
			[-1 * sin_y, 0, cos_y]]

	m_z = [[cos_z, -1 * sin_z, 0],
			[sin_z, cos_z, 0],
			[0, 0, 1]]

	mx = np.matrix(m_x)
	my = np.matrix(m_y)
	mz = np.matrix(m_z)

	m = mx * my * mz
	#print m
	for i in range(len(neuron)):
		x, y, z, r = neuron[i]
		v = np.matrix([x, y, z]).transpose()
		rotated_v = m * v
		x, y, z = rotated_v.transpose().tolist()[0]
		neuron[i] = [x, y, z, r]


def translate(obj, location):
	x_l, y_l, z_l = location
	for i in range(len(obj)):
		x, y, z, r = obj[i]
		obj[i] = [x + x_l, y + y_l, z + z_l, r]

def find_bounding_box(obj):
	min_x = max_x = obj[0][0]
	min_y = max_y = obj[0][1]
	min_z = max_z = obj[0][2]

	for i in range(len(obj)):
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

def cut_vascular(vascular, neuron):
	min_x, max_x, min_y, max_y, min_z, max_z = find_bounding_box(neuron)
	min_x -= 5
	min_y -= 5
	min_z -= 5

	max_x += 5
	max_y += 5
	max_z += 5

	cut_vascular = []
	for el in vascular:
		x, y, z, _ = el
		if x < min_x or x > max_x:
			continue
		if y < min_y or y > max_y:
			continue
		if z < min_z or z > max_z:
			continue
		cut_vascular.append(el)
	return cut_vascular

def distance(n, v):
	a = np.array(n[:3])
	b = np.array(v[:3])
	d = np.linalg.norm(a - b)
	return d

def sort_vascular(vascular):
	vascular.sort(key = lambda v:v[0])

def collide(n, v, threshold_distance):
		rsum = n[3] + v[3] + threshold_distance
		if abs(n[0] - v[0]) > rsum:
			return False
		if abs(n[1] - v[1]) > rsum:
			return False
		if abs(n[2] - v[2]) > rsum:
			return False
		if distance(n, v) <= rsum:
			return True
		return False

def separate_vascular(vascular, threshold):
	small_vascular = []
	big_vascular = []
	for v in vascular:
		if v[3] < threshold:
			small_vascular.append(v)
		else:
			big_vascular.append(v)
	return small_vascular, big_vascular

def find_nearest_points(vascular, neuron, threshold_distance):
	collisions = []

	BIG_VASCULAR_R = 3
	sort_vascular(vascular)
	vascular, big_vascular_nodes = separate_vascular(vascular, BIG_VASCULAR_R)
	#print ("Small: %i, Big: %i" % (len(vascular), len(big_vascular_nodes)))

	for n in neuron:
		found = False
		for v in big_vascular_nodes:
			if collide(n, v, threshold_distance):
				collisions.append(n)
				found = True
				break
		if found:
			continue
		base_idx = bisect.bisect(vascular, n)
		max_x_distance = BIG_VASCULAR_R + n[3] + threshold_distance
		cur_idx = base_idx
		while cur_idx < len(vascular) and abs(vascular[cur_idx][0]-n[0]) < max_x_distance:
			v = vascular[cur_idx]
			if collide(n, v, threshold_distance):
				collisions.append(n)
				found = True
				break
			cur_idx += 1
		if found:
			continue
		cur_idx = base_idx - 1
		while cur_idx >= 0 and abs(vascular[cur_idx][0] - n[0]) < max_x_distance:
			v = vascular[cur_idx]
			if collide(n, v, threshold_distance):
				collisions.append(n)
				break
			cur_idx -= 1

	return collisions


def get_vascular(vascular_filename):
	print("Read vascular data...")
	vascular = read_balls(vascular_filename)
	translate(vascular, [1, -15, 19])
	swap_x_y(vascular)

	return vascular

def aggregate(vascular_filename, neuron_filename, location, rotation, results_filename, threshold_distance, vascular = None):
	if vascular is None:
		vascular = get_vascular(vascular_filename)
	#max_r = max(vascular, key=lambda x : x[3])
	#print max_r
	# print("Read neuron data...")
	neuron = read_balls(neuron_filename)

	#print find_bounding_box(vascular)
	#print find_bounding_box(neuron)

	# print("Swap x y...")
	swap_x_y(neuron)
	# print("Rotate neuron...")
	rotate(neuron, rotation)
	# print("Translate neuron...")
	translate(neuron, location)

	# print("Cut vascular data...")
	vascular = cut_vascular(vascular, neuron)

	# print("Find nearest points...")
	collisions = find_nearest_points(vascular, neuron, threshold_distance)

	collisions_str = create_collision_str(collisions)
	run_id = "run_1"
	neuron_id = os.path.basename(neuron_filename)
	vascular_id = os.path.basename(vascular_filename)
	neuron_location = "{0} {1} {2}".format(*location)
	neuron_rotation = "{0} {1} {2}".format(*rotation)
	collisions_count = len(collisions)
	line = "{run_id},{neuron_id},{vascular_id},{neuron_location},{neuron_rotation},{collisions_count},{collisions_str}\n".format(**locals())
	with open(results_filename, "a") as f:
		f.write(line)

	print("Done!")
	return 0

def main(argv):
	if len(argv) < 6:
		print("Usage: %s <vascular data> <neuron data> <location> <rotation> <results file> [threshold distance]" % argv[0])
		return 1

	vascular_filename = argv[1]
	neuron_filename = argv[2]
	location = [int(a) for a in argv[3].split(",")]
	rotation = [int(a) for a in argv[4].split(",")]
	results_filename = argv[5]

	threshold_distance = 0
	if len(argv) >= 7:
		threshold_distance = int(argv[6])


	aggregate(vascular_filename, neuron_filename, location, rotation, results_filename, threshold_distance)


if __name__ == "__main__":
	start_time = time.time()
	main(sys.argv)
	end_time = time.time()
	print("Total time: %i seconds" % int(end_time - start_time))

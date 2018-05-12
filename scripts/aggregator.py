import sys, os
import math
import numpy as np


def read_balls(fname):
	res = []

	for line in open(fname, "rb"):
		if len(line) <= 1:
			pass
		x, y, z, r = [float(a) for a in line.split(",")]
		res.append([x, y, z, r])
	return res

def swap_x_y(obj):
	for i in xrange(len(obj)):
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
	for i in xrange(len(neuron)):
		x, y, z, r = neuron[i]
		v = np.matrix([x, y, z]).transpose()
		rotated_v = m * v
		x, y, z = rotated_v.transpose().tolist()[0]
		neuron[i] = [x, y, z, r]
	

def translate(obj, location):
	x_l, y_l, z_l = location
	for i in xrange(len(obj)):
		x, y, z, r = obj[i]
		obj[i] = [x + x_l, y + y_l, z + z_l, r]
		
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
	xn, yn, zn, rn = n
	xv, yv, zv, rv = v

	d = (xn-xv)**2 + (yn-yv)**2 + (zn-zv)**2
	#d = d ** 0.5
	return d

def find_nearest_points(vascular, neuron):
	i = 0
	print "len(neuron): ", len(neuron)
	for n in neuron:
		i += 1
		if i % 100 == 0:
			print i
		for v in vascular:
			if abs(n[0] - v[0]) > 3:
				continue
			if abs(n[1] - v[1]) > 3:
				continue
			if abs(n[2] - v[2]) > 3:
				continue
			if distance(n, v) < 1:
				print n, v

def main(argv):
	if len(argv) != 6:
		print "Usage: %s <vascular data> <neuron data> <location> <rotation> <results file>" % argv[0]
		return 1
	
	vascular_filename = argv[1]
	neuron_filename = argv[2]
	location = [int(a) for a in argv[3].split(",")]
	rotation = [int(a) for a in argv[4].split(",")]
	results_filename = argv[5]

	
	print "Read vascular data..."
	vascular = read_balls(vascular_filename)
	print "Read neuron data..."
	neuron = read_balls(neuron_filename)

	#print find_bounding_box(vascular)
	#print find_bounding_box(neuron)

	print "Swap x y..."
	swap_x_y(neuron)
	print "Rotate neuron..."
	rotate(neuron, rotation)
	print "Translate neuron..."
	translate(neuron, location)

	print "Cut vascular data..."
	vascular = cut_vascular(vascular, neuron)

	print "Find nearest points..."
	find_nearest_points(vascular, neuron)

	print "Done!"
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))

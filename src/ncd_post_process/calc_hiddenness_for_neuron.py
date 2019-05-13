#!/usr/bin/python

import sys, os


def calc_dist(us):
	max_u = max(us)
	dist = [0] * (max_u + 1)

	for u in us:
		dist[u] += 1

	return dist

def distance(p1, p2, threshold, threshold_square):
	if abs(p1[0] - p2[0]) > threshold:
		return False
	if abs(p1[1] - p2[1]) > threshold:
		return False
	if abs(p1[2] - p2[2]) > threshold:
		return False
	d = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2
	if d < threshold_square:
		return True
	return False

def main(argv):
	if len(argv) != 4:
		print("Usage: %s <neuron_path> <u radius> <output filename>" % argv[0])
		return 1
	
	neuron_path = argv[1]
	u_r = int(argv[2], 10)
	output_filename = argv[3]


	neuron = []
	for line in open(neuron_path, "r"):
		x, y, z, r = [float(x) for x in line.split(",")]
		neuron.append((x, y, z))

	neuron = sorted(neuron, key=lambda x : x[0])
	vertex_cnt = len(neuron)
	us = [0] * vertex_cnt
	u_r_square = u_r * u_r

	for i in range(vertex_cnt):
		n1_x = neuron[i][0]
		for j in range(i+1, vertex_cnt):
			if n1_x + u_r < neuron[j][0]:
				break
			if distance(neuron[i], neuron[j], u_r, u_r_square):
				us[i] += 1
				us[j] += 1

	distribution = calc_dist(us)
	with open(output_filename, "w") as f:
		for el in distribution:
			f.write(str(el) + "\n")

	sum_u = sum(us)
	print ("Average hiddenness: " + str(sum_u / vertex_cnt))

	print ("Done!")

if __name__ == "__main__":
	main(sys.argv)

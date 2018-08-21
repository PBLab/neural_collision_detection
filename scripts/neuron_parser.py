#!/usr/bin/python
from __future__ import print_function
import os, sys
import numpy as np
import math
import find_enclosing_box
from parser import ResultsParser
from plotter import plot_2d

SHRINK_FACTOR = 5

def create_res_arr(bb):
	xmin, xmax, ymin, ymax, zmin, zmax = [int(x) for x in bb]
	x_size = (xmax - xmin) / SHRINK_FACTOR + 2
	y_size = (ymax - ymin) / SHRINK_FACTOR + 2
	z_size = (zmax - zmin) / SHRINK_FACTOR + 2

	res = np.zeros((x_size, y_size, z_size), np.int32)
	print("Result array size:", x_size, y_size, z_size, " Total: ",  x_size * y_size * z_size)
	return res, xmin / SHRINK_FACTOR, ymin / SHRINK_FACTOR, zmin / SHRINK_FACTOR


def create_column_graph(collision_arr, resolution, fname):
	max_collisions = collision_arr[0][0][0]
	for i in range(len(collision_arr)):
		for j in range(len(collision_arr[0])):
			for k in range(len(collision_arr[0][0])):
				cur_collisions = collision_arr[i][j][k]
				if max_collisions < cur_collisions:
					max_collisions = cur_collisions

	graph = []
	graph.append(list(range(0, max_collisions, resolution)))
	graph.append([0] * (max_collisions / resolution + 1))

	for i in range(len(collision_arr)):
		for j in range(len(collision_arr[0])):
			for k in range(len(collision_arr[0][0])):
				cur_collisions = collision_arr[i][j][k]
				if cur_collisions == 0:
					#continue
					pass
				graph[1][cur_collisions / resolution] += 1
	print(graph[0])
	print(graph[1])

	with open(fname, "ab") as f:
		f.write(",".join([str(x) for x in graph[0]]))
		f.write("\n")
		f.write(",".join([str(x) for x in graph[1]]))
		f.write("\n")
		f.write("\n")

def my_sum(arr1, arr2):
	for i in range(len(arr1)):
		for j in range(len(arr1[i])):
			arr1[i][j] = arr1[i][j] + arr2[i][j]
	return arr1


def parse_neuron(parser, neuron_id, output_dir):
	full_path = "/state/partition1/home/yoavj/neurons/{neuron_id}_balls.csv".format(**locals())
	print(full_path)

	bb = find_enclosing_box.get_bb(full_path)
	print("Bounding Box:", bb)

	arr, xmin, ymin, zmin = create_res_arr(bb)

	#rp = parser.where(lambda x: x.run_id == "agg_distance_5").where(lambda x : x.neuron_id == neuron_id)
	rp = parser.where(lambda x : x.neuron_id == neuron_id)
	for r in rp:
		cols = r.get_collisions_on_neuron()
		for c in cols:
			# SWAP X Y
			x, y, z = c[1], c[0], c[2]
			shrinked_x = int(x) / SHRINK_FACTOR
			shrinked_y = int(y) / SHRINK_FACTOR
			shrinked_z = int(z) / SHRINK_FACTOR
			arr_x_idx = shrinked_x - xmin
			arr_y_idx = shrinked_y - ymin
			arr_z_idx = shrinked_z - zmin
			arr[arr_x_idx][arr_y_idx][arr_z_idx] += 1

	output_npy = os.path.join(output_dir, "collisions_array_{neuron_id}.npy".format(**locals()))
	np.save(output_npy, arr)
	GRAPH_RESOLUTION = 5
	output_csv = os.path.join(output_dir, "collisions_chart.csv")

	create_column_graph(arr, GRAPH_RESOLUTION, output_csv)

	for i in range(1, len(arr)):
		#print arr[i]
		arr[0] = my_sum(arr[0], arr[i])
		#plot_2d(arr[i], output_fname)
	output_fname = os.path.join(output_dir, "{neuron_id}_0_plot.png".format(**locals()))
	for i in range(len(arr[0])):
		for j in range(len(arr[0][i])):
			if arr[0][i][j] > 0:
				arr[0][i][j] += 100
	plot_2d(arr[0], output_fname)


def main(argv):
	if len(argv) < 3:
		print("Usage: %s <input file> <output directory>" % argv[0])
		return 1
	
	input_filename = argv[1]
	output_dir = argv[2]

	os.system("mkdir {0}".format(output_dir))

	parser = ResultsParser(open(input_filename).readlines())
	print("Total results: ", len(parser))

	for neuron_id in parser.get_neurons():
		parse_neuron(parser, neuron_id, output_dir)
		print("\n")

if __name__ == "__main__":
	main(sys.argv)

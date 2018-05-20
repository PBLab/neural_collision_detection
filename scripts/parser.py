#!/usr/bin/python

import os, sys
import numpy as np
import math
import find_enclosing_box

SHRINK_FACTOR = 5

def get_rotation_matrix(rotation):
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
	return m

class Result:
	def __init__(self, line):
		if isinstance(line, str):
			self._init_from_string(line)
		elif isinstance(line, Result):
			self._init_from_result(line)

	@staticmethod
	def back_translate_collision(collision, translation):
		x, y, z = collision
		xt, yt, zt = translation
		return [x - xt, y - yt, z - zt]

	@staticmethod
	def back_rotate_collision(collision, rotation):
		m = get_rotation_matrix(rotation)
		m = np.linalg.inv(m)

		x, y, z = collision

		v = np.matrix([x, y, z]).transpose()
		rotated_v = m * v
		return rotated_v.transpose().tolist()[0]

	# This returns on .obj, not .csv
	def get_collisions_on_neuron(self):
		cols = []
		for collision in self.collisions:
			collision = self.back_translate_collision(collision, self.translation)
			collision = self.back_rotate_collision(collision, self.rotation)
			cols.append(collision)
		return cols

	def _init_from_result(self, res):
		self.run_id = res.run_id
		self.neuron_id = res.neuron_id
		self.vascular_id = res.vascular_id
		self.translation = res.translation
		self.rotation = res.rotation
		self.collisions = list(res.collisions)

	def _init_from_string(self, line):
		splitted = line.split(",")
		if len(splitted) != 6:
			raise Exception("bad line")

		self.run_id = splitted[0]
		self.neuron_id = splitted[1]
		self.vascular_id = splitted[2]
		self.translation = [float(x) for x in splitted[3].split(" ")]
		self.rotation = [float(x) for x in splitted[4].split(" ")]
		self.collisions = []
		for col in splitted[5].split("|"):
			self.collisions.append([float(x) for x in col.split(" ")])

	def _get_collision_string(self):
		res = ""
		for col in self.collisions:
			x, y, z = [str(a) for a in col]
			col = " ".join([x, y, z])
			res += col + "|"
		return res[:-1]

	def __str__(self):
		col_str = self._get_collision_string()
		translation_str = " ".join([str(a) for a in self.translation])
		rotation_str = " ".join([str(a) for a in self.rotation])
		return "{0},{1},{2},{3},{4},{5}".format(self.run_id, self.neuron_id, self.vascular_id, translation_str, rotation_str, col_str)

class ResultsParser:
	def __init__(self, lines):
		self.results = [Result(l) for l in lines]
		self.idx = 0
		self.total_len = len(self.results)

	def __len__(self):
		return self.total_len

	def __iter__(self):
		self.idx = 0
		return self

	def next(self):
		if self.idx >= self.total_len:
			raise StopIteration
		self.idx += 1
		return self.results[self.idx - 1]

	def where(self, f):
		results = []
		for r in self.results:
			if f(r):
				results.append(r)
		return ResultsParser(results)

	def get_neurons(self):
		n = []
		for res in self.results:
			n.append(res.neuron_id)

		return list(set(n))
		
	def __str__(self):
		return "\n".join([str(x) for x in self.results])

def create_res_arr(bb):
	xmin, xmax, ymin, ymax, zmin, zmax = [int(x) for x in bb]
	x_size = (xmax - xmin) / SHRINK_FACTOR + 2
	y_size = (ymax - ymin) / SHRINK_FACTOR + 2
	z_size = (zmax - zmin) / SHRINK_FACTOR + 2

	res = []
	for i in xrange(x_size):
		res.append([])
		for j in xrange(y_size):
			res[i].append([])
			for k in xrange(z_size):
				res[i][j].append(0)
	print x_size * y_size * z_size
	return res, xmin / SHRINK_FACTOR, ymin / SHRINK_FACTOR, zmin / SHRINK_FACTOR


def parse_neuron(parser, neuron_id):
	full_path = "/state/partition1/home/yoavj/neurons/{neuron_id}_balls.csv".format(**locals())

	print full_path

	bb = find_enclosing_box.get_bb(full_path)
	print bb

	arr, xmin, ymin, zmin = create_res_arr(bb)

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
			#print shrinked_x, shrinked_y, shrinked_z
			#print arr_x_idx, arr_y_idx, arr_z_idx
			arr[arr_x_idx][arr_y_idx][arr_z_idx] += 1

	max_col = arr[0][0][0]
	cnt = 0
	total_col = 0

	for i in xrange(len(arr)):
		for j in xrange(len(arr[0])):
			for k in xrange(len(arr[0][0])):
				cur_col = arr[i][j][k]
				if max_col < cur_col:
					max_col = cur_col
				if cur_col > 0:
					cnt += 1
				total_col += cur_col
	avg = total_col / cnt
	print "max: {max_col}, avg: {avg}, total: {total_col}, cnt: {cnt}".format(**locals())

def main(argv):
	if len(argv) < 2:
		print "Usage: %s <input file>" % argv[0]
		return 1
	
	input_filename = argv[1]

	parser = ResultsParser(open(input_filename).readlines())
	print len(parser)

	for neuron_id in parser.get_neurons():
		parse_neuron(parser, neuron_id)

	#rp = parser.where(lambda x: x.run_id == "agg_distance_0").where(lambda x : len(x.collisions) < 4)
	#for r in rp:
		#print r
		#print r.get_collisions_on_neuron()
	#print "\n".join(parser.where(lambda x: x.run_id == "agg_distance_0").where(lambda x : len(x.collisions) < 6))
	#print "\n".join(parser.where(lambda x: x.startswith("agg_distance_0,")).where(lambda x : len(x.split(",")[COL_COLLISIONS].split("|")) <= 11).lines)
	
if __name__ == "__main__":
	main(sys.argv)

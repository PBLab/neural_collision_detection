import os, sys
import math
import numpy as np


def rotate_array(arr, rotation):
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
	new_arr = []
	for p in arr:
		x, y, z = p
		v = np.matrix([x, y, z]).transpose()
		rotated_v = m * v
		x, y, z = rotated_v.transpose().tolist()[0]
		new_arr.append([x, y, z])
	return new_arr

def create_box(x_low, x_high, y_low, y_high, z_low, z_high):
	vertices = [
				[ x_low, y_low, z_low ],
				[ x_high, y_low, z_low ],
				[ x_high, y_high, z_low ],
				[ x_low, y_high, z_low ],
				[ x_low, y_low, z_high ],
				[ x_high, y_low, z_high ],
				[ x_high, y_high, z_high ],
				[ x_low, y_high, z_high ],
			   ]

	faces = [
				[ 1, 5, 6 ],
				[ 1, 6, 2 ],
				[ 2, 6, 7 ],
				[ 2, 7, 3 ],
				[ 3, 7, 8 ],
				[ 3, 8, 4 ],
				[ 4, 8, 5 ],
				[ 4, 5, 1 ],
				[ 6, 8, 7 ],
				[ 6, 5, 8 ],
				[ 4, 2, 3 ],
				[ 4, 1, 2 ],
		    ]

	return (vertices, faces)


class ObjData(object):
	def __init__(self):
		self.vertices = []
		self.faces = []

	def __str__(self):
		vertices = "\n".join([str(x) for x in self.vertices])
		faces = "\n".join([str(x) for x in self.faces])
		return "Vertices:\n{vertices}\n\n\nFaces:\n{faces}".format(**locals())

	def add_shape(self, shape):
		vertices, faces = shape
		addend = len(self.vertices)

		faces = [[f[0] + addend, f[1] + addend, f[2] + addend] for f in faces]
		self.vertices += vertices
		self.faces += faces

	def dump_to_file(self, fname):
		with open(fname ,"wb") as fh:
			for v in self.vertices:
				fh.write("v %s %s %s\n" % (v[0], v[1], v[2]))
			for f in self.faces:
				fh.write("f %i %i %i\n" % (f[0], f[1], f[2]))
			fh.write("\n")

	def rotate(self, rotation):
		self.vertices = rotate_array(self.vertices, rotation)
		

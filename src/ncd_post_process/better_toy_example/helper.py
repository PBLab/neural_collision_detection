#!/state/partition1/apps/python/anaconda2/bin/python
import sys
sys.path.append("..")
from create_cube import *
import numpy as np



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


def generate_grid(start, end, step, width, fname):
	o = ObjData()

	for x in np.arange(start, end, step):
		for y in np.arange(start, end, step):
			b = create_box(x, x + width, y, y+width, start, end)
			o.add_shape(b)

	for x in np.arange(start, end, step):
		for z in np.arange(start, end, step):
			b = create_box(x, x + width, start, end, z, z + width)
			o.add_shape(b)

	for y in np.arange(start, end, step):
		for z in np.arange(start, end, step):
			b = create_box(start, end, y, y + width, z, z + width)
			o.add_shape(b)

	o.dump_to_file(fname)

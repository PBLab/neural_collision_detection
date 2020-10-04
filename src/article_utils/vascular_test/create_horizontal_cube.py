from __future__ import print_function
import os, sys

def create_box(x_low, x_high, y_low, y_high, z_low, z_high):
	v = [
			[x_low, y_low, z_low],
			[x_high, y_low, z_low],
			[x_high, y_high, z_low],
			[x_low, y_high, z_low],
			[x_low, y_low, z_high],
			[x_high, y_low, z_high],
			[x_high, y_high, z_high],
			[x_low, y_high, z_high],
		]

	f = [
			[1, 5, 6],
			[1, 6, 2],
			[2, 6, 7],
			[2, 7, 3],
			[3, 7, 8],
			[3, 8, 4],
			[4, 8, 5],
			[4, 5, 1],
			[6, 8, 7],
			[6, 5, 8],
			[4, 2, 3],
			[4, 1, 2],
		]
	return (v, f)


def create_box_obj(x_low, x_high, y_low, y_high, z_low, z_high, filename):
	cube = """
v {x_low} {y_low} {z_low}
v {x_high} {y_low} {z_low}
v {x_high} {y_high} {z_low}
v {x_low} {y_high} {z_low}
v {x_low} {y_low} {z_high}
v {x_high} {y_low} {z_high}
v {x_high} {y_high} {z_high}
v {x_low} {y_high} {z_high}
f 1 5 6
f 1 6 2
f 2 6 7
f 2 7 3
f 3 7 8
f 3 8 4
f 4 8 5
f 4 5 1
f 6 8 7
f 6 5 8
f 4 2 3
f 4 1 2
	""".format(**locals())

	with open(filename, "w") as f:
		f.write(cube)


def create_cube(center, r, h, filename):
	x, y, z = center
	x_low = x - h / 2
	x_high = x + h / 2
	y_low = y - r
	y_high = y + r
	z_low = z - r
	z_high = z + r

	create_box_obj(x_low, x_high, y_low, y_high, z_low, z_high, filename)

def main(argv):
	if len(argv) < 4:
		print("Usage: %s <output file> <radius> <height>" % argv[0])
		return 1

	filename = argv[1]
	r = float(argv[2])
	h = int(argv[3])

	create_cube((0, 0, 0), r, h, filename)


if __name__ == "__main__":
	main(sys.argv)

#!/state/partition1/apps/python/anaconda2/bin/python
import sys
sys.path.append("..")
from obj_operations import *
from create_cube import *
import numpy as np
import random

def generate_grid(start, end, step, width, empty, rotation, fname):
	o = ObjData()

	for x in np.arange(start, end, step):
		for y in np.arange(start, end, step):
			if x >= empty[0] and x <= empty[1] and y >= empty[2] and y <= empty[3]:
				continue
			b = create_box(x, x + width, y, y+width, start, end)
			o.add_shape(b)

	for x in np.arange(start, end, step):
		for z in np.arange(start, end, step):
			if x >= empty[0] and x <= empty[1] and z >= empty[4] and z <= empty[5]:
				continue
			b = create_box(x, x + width, start, end, z, z + width)
			o.add_shape(b)

	for y in np.arange(start, end, step):
		for z in np.arange(start, end, step):
			if y >= empty[2] and y <= empty[3] and z >= empty[4] and z <= empty[5]:
				continue
			b = create_box(start, end, y, y + width, z, z + width)
			o.add_shape(b)
		
	o.rotate(rotation)
	o.dump_to_file(fname)

def generate_centers(start, end, amount, rotation, fname):
	centers = []
	for i in xrange(amount):
		x = random.randrange(start, end)
		y = random.randrange(start, end)
		z = random.randrange(start, end)
		centers.append((x, y, z))

	centers = rotate_array(centers, rotation)

	with open(fname, "wb") as f:
		for c in centers:
			f.write("%i,%i,%i\n" % (c[0], c[1], c[2]))

def run_ncd(grid_fname, box_fname, centers_fname):
	ncd_path = "~/ncd"
	output_dir = "out"
	output_file = "res.txt"
	cmd_delete = "rm -rf {output_dir} {output_file}".format(**locals())
	cmd = "{ncd_path} -m batch -V {grid_fname} -N {box_fname} -o {output_dir} -f {output_file} -i {centers_fname} -z -t 12 -c 1".format(**locals())
	cmd_check = "ls -l {output_dir}".format(**locals())
	print cmd_delete
	print cmd
	print cmd_check

	input_text = raw_input("Run? [Y/n]")
	if len(input_text) > 0 and input_text.lower()[0] == 'n':
		return

	
	os.system(cmd_delete)
	os.system(cmd)
	os.system(cmd_check)

def generate_random_corner(start, end, empty_size):
	x_start = start + empty_size[0]
	x_end = end - empty_size[0]

	y_start = start + empty_size[0]
	y_end = end - empty_size[0]

	z_start = start + empty_size[0]
	z_end = end - empty_size[0]

	x = random.randrange(x_start, x_end)
	y = random.randrange(y_start, y_end)
	z = random.randrange(z_start, z_end)

	return x, y, z

def main():
	GRID_SIZE = 120
	START = 0 - GRID_SIZE/2
	END = 0 + GRID_SIZE/2
	STEP = 2
	WIDTH = 1
	EMPTY_SIZE   = (14, 40, 14)
	#EMPTY_CORNER = (30, 40, 50)
	GRID_ROTATION = (0, 0, 45)
	#GRID_ROTATION = generate_random_rotation()
	EMPTY_CORNER = generate_random_corner(START, END, EMPTY_SIZE)
	BOX_MARGIN   = 7
	BOX_CENTER   = (0, 0, 0)
	BOX_SIZE     = (EMPTY_SIZE[0] - BOX_MARGIN, EMPTY_SIZE[1] - BOX_MARGIN, EMPTY_SIZE[2] - BOX_MARGIN)
	CENTERS_MARGIN = 10
	CENTERS_AMOUNT = 100000
	EMPTY = (EMPTY_CORNER[0], EMPTY_CORNER[0] + EMPTY_SIZE[0],
			 EMPTY_CORNER[1], EMPTY_CORNER[1] + EMPTY_SIZE[1],
			 EMPTY_CORNER[2], EMPTY_CORNER[2] + EMPTY_SIZE[2])
	GRID_FNAME = "grid.obj"
	BOX_FNAME = "box.obj"
	CENTERS_FNAME = "centers.csv"
	PARAMS_FNAME = "params.txt"

	generate_grid(START, END, STEP, WIDTH, EMPTY, GRID_ROTATION, GRID_FNAME)

	create_box_obj(BOX_CENTER[0] - BOX_SIZE[0] / 2, BOX_CENTER[0] + BOX_SIZE[0] / 2,
				   BOX_CENTER[1] - BOX_SIZE[1] / 2, BOX_CENTER[1] + BOX_SIZE[1] / 2,
				   BOX_CENTER[2] - BOX_SIZE[2] / 2, BOX_CENTER[2] + BOX_SIZE[2] / 2,
				   BOX_FNAME)

	generate_centers(START + CENTERS_MARGIN, END - CENTERS_MARGIN, CENTERS_AMOUNT, GRID_ROTATION, CENTERS_FNAME)

	EMPTY_CENTER = (EMPTY_CORNER[0] + EMPTY_SIZE[0]/2, EMPTY_CORNER[1] + EMPTY_SIZE[1]/2, EMPTY_CORNER[2] + EMPTY_SIZE[2]/2)
	EMPTY_CORNER_AFTER_ROTATION = rotate_array([EMPTY_CORNER], GRID_ROTATION)[0]
	EMPTY_CENTER_AFTER_ROTATION = rotate_array([EMPTY_CENTER], GRID_ROTATION)[0]
	params = "\
Grid:\n\t\t{START} -> {END}, STEP = {STEP}, WIDTH = {WIDTH}, ROTATION = {GRID_ROTATION}\n\
Empty:\n\t\tCorner: {EMPTY_CORNER}, Size: {EMPTY_SIZE}\n\
\n\t\tAfter Rotation: Corner: {EMPTY_CORNER_AFTER_ROTATION}, Center: {EMPTY_CENTER_AFTER_ROTATION}\n\
Box:\n\t\tCenter: {BOX_CENTER}, Size: {BOX_SIZE}\n\
Centers:\n\t\t{CENTERS_AMOUNT} with {CENTERS_MARGIN} margin\n\
".format(**locals())
	print params
	with open(PARAMS_FNAME, "wb") as f:
		f.write(params)

	run_ncd(GRID_FNAME, BOX_FNAME, CENTERS_FNAME)
	print params


if __name__ == "__main__":
	main()

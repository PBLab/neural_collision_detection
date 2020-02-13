#!/state/partition1/apps/python/anaconda2/bin/python
import sys
sys.path.append("..")
from obj_operations import *
from create_cube import *
import numpy as np
import random
import datetime


def parse_results_centers_bounding_box(res_fname):
	min_x = None
	min_y = None
	min_z = None

	max_x = None
	max_y = None
	max_z = None
	with open(res_fname, "rb") as f:
		for l in f:
			els = l.split(",")
			if len(els) < 7:
				continue
			location = [int(x) for x in els[1:4]]
			rotation = [int(x) for x in els[4:7]]
			if min_x is None or min_x > location[0]:
				min_x = location[0]
			if min_y is None or min_y > location[1]:
				min_y = location[1]
			if min_z is None or min_z > location[2]:
				min_z = location[2]

			if max_x is None or max_x < location[0]:
				max_x = location[0]
			if max_y is None or max_y < location[1]:
				max_y = location[1]
			if max_z is None or max_z < location[2]:
				max_z = location[2]

	return (min_x, max_x, min_y, max_y, min_z, max_z)

def parse_results_rotation(res_fname, real_rotation):
	BASE_OFFSET = 16
	distances_x = [0] * (BASE_OFFSET * 2 + 1)
	distances_y = [0] * (BASE_OFFSET * 2 + 1)
	distances_z = [0] * (BASE_OFFSET * 2 + 1)
	helper = [0] * (BASE_OFFSET * 2 + 1)
	helper[BASE_OFFSET] = 1
	with open(res_fname, "rb") as f:
		for l in f:
			els = l.split(",")
			if len(els) < 7:
				continue
			rotation = [int(x) for x in els[4:7]]

			if (rotation[2] > 170):
				continue
			dist_x = (real_rotation[0] - rotation[0])
			dist_y = (real_rotation[1] - rotation[1])
			dist_z = (real_rotation[2] - rotation[2])

			distances_x[dist_x + BASE_OFFSET] += 1
			distances_y[dist_y + BASE_OFFSET] += 1
			distances_z[dist_z + BASE_OFFSET] += 1


	print "Distance from real rotation x: {distances_x}".format(**locals())
	print "Distance from real rotation y: {distances_y}".format(**locals())
	print "Distance from real rotation z: {distances_z}".format(**locals())
	print "========= helper ============: {helper}".format(**locals())
	print "(BASE_OFFSET: {BASE_OFFSET})".format(**locals())
	FNAME_X = "distances_x"
	FNAME_Y = "distances_y"
	FNAME_Z = "distances_z"
	append_results_to_file(distances_x, FNAME_X)
	append_results_to_file(distances_y, FNAME_Y)
	append_results_to_file(distances_z, FNAME_Z)

	#return distances_x, distances_y, distances_z

def append_results_to_file(results, fname):
	with open(fname, "a") as f:
		f.write(",".join(["%03s"%x for x in results]) + "\n")

def parse_results_avg(res_fname):
	cnt_location = 0
	cnt_rotation = 0
	avg_location = [0.0,0.0,0.0]
	avg_rotation = [0.0,0.0,0.0]
	with open(res_fname, "rb") as f:
		for l in f:
			els = l.split(",")
			if len(els) < 7:
				continue
			location = [int(x) for x in els[1:4]]
			rotation = [int(x) for x in els[4:7]]
			cnt_location += 1
			avg_location[0] += location[0]
			avg_location[1] += location[1]
			avg_location[2] += location[2]

			if (rotation[2] > 170):
				continue
			cnt_rotation += 1
			avg_rotation[0] += rotation[0]
			avg_rotation[1] += rotation[1]
			avg_rotation[2] += rotation[2]

	avg_location[0] /= cnt_location
	avg_location[1] /= cnt_location
	avg_location[2] /= cnt_location

	avg_rotation[0] /= cnt_rotation
	avg_rotation[1] /= cnt_rotation
	avg_rotation[2] /= cnt_rotation

	print "Average location: {avg_location}".format(**locals())
	print "Average rotation: {avg_rotation}".format(**locals())


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

def run_ncd(grid_fname, box_fname, centers_fname, results_fname, force_run = False):
	#ncd_path = "~/ncd"
	ncd_path = "~/ncd_toy_example"
	output_dir = "out"
	output_file = results_fname
	cmd_delete = "rm -rf {output_dir} {output_file}".format(**locals())
	cmd = "{ncd_path} -m batch -V {grid_fname} -N {box_fname} -o {output_dir} -f {output_file} -i {centers_fname} -z -t 12 -c 1".format(**locals())
	#cmd_check = "ls -l {output_dir}".format(**locals())
	print cmd_delete
	print cmd
	#print cmd_check

	if not force_run:
		input_text = raw_input("Run? [Y/n]")
		if len(input_text) > 0 and input_text.lower()[0] == 'n':
			raise Exception("Aborted")


	os.system(cmd_delete)
	os.system(cmd)
	#os.system(cmd_check)

def generate_random_rotation():
	x = random.randrange(-5, 5)
	y = random.randrange(-5, 5)
	z = random.randrange(20, 160)

	return (x, y, z)

def generate_random_corner(start, end, empty_size):
	x_start = start + 2
	x_end = end - empty_size[0] - 2

	y_start = start + 2
	y_end = end - empty_size[1] - 2

	z_start = start + 2
	z_end = end - empty_size[2] - 2

	x = random.randrange(x_start, x_end)
	y = random.randrange(y_start, y_end)
	z = random.randrange(z_start, z_end)

	return x, y, z

def main():
	FORCE_RUN = True
	GRID_SIZE = 160
	START = 0 - GRID_SIZE/2
	END = 0 + GRID_SIZE/2
	STEP = 2
	WIDTH = 1
	# Needs to be multiple of 7
	EMPTY_SIZE   = (21, 126, 56) # multiplty of 7
	#EMPTY_SIZE   = (20, 125, 55) # multiply of 5
	#EMPTY_CORNER = (30, 40, 50)
	#GRID_ROTATION = (0, 0, 45)
	GRID_ROTATION = generate_random_rotation()
	GRID_ROTATION = (0, 0, 0)
	EMPTY_CORNER = generate_random_corner(START, END, EMPTY_SIZE)
	BOX_MARGIN   = [EMPTY_SIZE[0] / 7, EMPTY_SIZE[1] / 7, EMPTY_SIZE[2] / 7]
	BOX_CENTER   = (0, 0, 0)
	BOX_SIZE     = (EMPTY_SIZE[0] - BOX_MARGIN[0], EMPTY_SIZE[1] - BOX_MARGIN[1], EMPTY_SIZE[2] - BOX_MARGIN[2])
	CENTERS_MARGIN = min(EMPTY_SIZE)
	CENTERS_AMOUNT = 600000
	EMPTY = (EMPTY_CORNER[0], EMPTY_CORNER[0] + EMPTY_SIZE[0],
			 EMPTY_CORNER[1], EMPTY_CORNER[1] + EMPTY_SIZE[1],
			 EMPTY_CORNER[2], EMPTY_CORNER[2] + EMPTY_SIZE[2])
	GRID_FNAME = "grid.obj"
	BOX_FNAME = "box.obj"
	CENTERS_FNAME = "centers.csv"
	RESULTS_FNAME = "res.txt"
	date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
	PARAMS_FNAME = "params_%s.txt" % date

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

	run_ncd(GRID_FNAME, BOX_FNAME, CENTERS_FNAME, RESULTS_FNAME, FORCE_RUN)
	print params

	min_x, max_x, min_y, max_y, min_z, max_z = parse_results_centers_bounding_box(RESULTS_FNAME)
	if min_x is None:
		print "No results found"
		return

	print "Centers bb:\t({min_x},{min_y},{min_z}) -> ({max_x},{max_y},{max_z})".format(**locals())

	t_min_x = min_x - BOX_SIZE[0]/2
	t_min_y = min_y - BOX_SIZE[1]/2
	t_min_z = min_z - BOX_SIZE[2]/2

	t_max_x = max_x + BOX_SIZE[0]/2
	t_max_y = max_y + BOX_SIZE[1]/2
	t_max_z = max_z + BOX_SIZE[2]/2

	print "Total bb:\t({t_min_x},{t_min_y},{t_min_z}) -> ({t_max_x},{t_max_y},{t_max_z})".format(**locals())
	empty_far_corner = [EMPTY_CORNER[i] + EMPTY_SIZE[i] for i in range(3)]
	print "Empty area:\t{EMPTY_CORNER} -> {empty_far_corner}".format(**locals())

	#parse_results_rotation(RESULTS_FNAME, GRID_ROTATION)

	############ Save output to dir 
	OUTPUT_DIR = "non_rotation_data_%s" % date
	os.system("mkdir " + OUTPUT_DIR)
	os.system("cp {RESULTS_FNAME} {OUTPUT_DIR}/{RESULTS_FNAME}".format(**locals()))
	os.system("cp {PARAMS_FNAME} {OUTPUT_DIR}/{PARAMS_FNAME}".format(**locals()))
	total_bb_fname = os.path.join(OUTPUT_DIR, "parsed_run.txt")
	with open(total_bb_fname, "wb") as f:
		f.write("({t_min_x},{t_min_y},{t_min_z}) -> ({t_max_x},{t_max_y},{t_max_z})\n".format(**locals()))
		f.write("{EMPTY_CORNER} -> {empty_far_corner}\n".format(**locals()))





if __name__ == "__main__":
	main()

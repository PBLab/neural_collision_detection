import os, sys
import plotter


def parse_line(line, use_x):
	if len(line) == 0:
		raise "empty line"
	splitted = line.split(",")
	if use_x:
		return int(splitted[2]), int(splitted[3]) # return y,z
	return int(splitted[1]), int(splitted[2]) # return x,y

#def plot_2d(value_array, output_filename, colormap = 'Reds'):

def create_heatmap(res, output_file):
	plotter.plot_2d(res, output_file, colormap = 'Greys')

def main(argv):
	if len(argv) < 3:
		print ("Usage : %s <input file> <object radius> <output file> [-r]" % argv[0])
		return

	input_file = argv[1]
	object_r = int(argv[2])
	output_file = argv[3]
	use_x = False
	if len(argv) > 4 and argv[4] == '-r':
		use_x = True

	accumulated_cells = []
	for i in range(1000):
		accumulated_cells.append([])
		for j in range(1000):
			accumulated_cells[i].append(0)

	with open(input_file, "r") as f:
		for line in f:
			if len(line) == 0:
				continue
			x, y = parse_line(line, use_x)
			for i in range(-object_r, object_r):
				for j in range(-object_r, object_r):
					accumulated_cells[x+i][y+j] += 1
			#print x, y
			#return

	res = []
	for i in range(1000):
		for j in range(1000):
			if accumulated_cells[i][j] != 0:
				res.append(((i,j),accumulated_cells[i][j]))
				#f.write("%i,%i: %i\n" % (i, j, accumulated_cells[i][j]))

	
	res = sorted(res, key=lambda el: el[0])
	res = sorted(res, key=lambda el: el[1])
	
	"""
	with open(output_file, "w") as f:
		for el in res:
			f.write("%i,%i: %i\n" % (el[0][0], el[0][1], el[1]))
	"""

	create_heatmap(accumulated_cells, output_file)

if __name__ == "__main__":
	main(sys.argv)

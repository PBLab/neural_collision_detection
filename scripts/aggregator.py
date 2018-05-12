import sys, os



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
	pass

def translate(obj, location):
	x_l, y_l, z_l = location
	for i in xrange(len(obj)):
		x, y, z, r = obj[i]
		obj[i] = [x + x_l, y + y_l, z + z_l, r]
		
def cut_vascular(vascular, neuron):
	pass

def find_nearest_points(vascular, neuron):
	pass

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
	print "Swap x y..."
	swap_x_y(neuron)
	print "Rotate neuron..."
	rotate(neuron, rotation)
	print "Translate neuron..."
	translate(neuron, location)
	print "Cut vascular data..."
	cut_vascular(vascular, neuron)

	print "Find nearest points..."
	find_nearest_points(vascular, neuron)

	print "Done!"
	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))

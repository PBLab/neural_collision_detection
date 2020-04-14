import sys, os


def main(argv):
	if len(argv) < 2:
		print ("Usage: %s <output file> <object length> [-r]" % argv[0])
		return

	output_filename = argv[1]
	object_length = int(argv[2])
	use_x = False
	if len(argv) >= 4 and argv[3] == "-r":
		print ("Using X axis instead of Z axis")
		use_x = True

	X_SIZE = 1000
	Y_SIZE = 1000
	Z_SIZE = 1000

	#OBJECT_LENGTH = 400

	SPACE = 10
	AXIS_SPACE = 20
	STEP = 2
	Z_STEP = 20


	cnt = 0
	f = open(output_filename, "w")
	for i in range(SPACE, X_SIZE - SPACE, STEP):
		for j in range(SPACE, Y_SIZE - SPACE, STEP):
			cnt += 1
			for k in range(object_length / 2 + AXIS_SPACE, Z_SIZE - object_length / 2 - AXIS_SPACE, Z_STEP):
				if use_x:
					f.write("%i, %i, %i\n" % (k, j, i))
				else:
					f.write("%i, %i, %i\n" % (i, j, k))

	print ("cnt = %i" % cnt)
				


if __name__ == "__main__":
	main(sys.argv)

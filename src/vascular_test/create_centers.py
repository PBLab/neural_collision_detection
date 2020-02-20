import sys, os


def main(argv):
	if len(argv) < 2:
		print ("Usage: %s <output file> [-r]" % argv[0])
		return

	output_filename = argv[1]
	use_x = False
	if len(argv) >= 3 and argv[2] == "-r":
		print ("Using X axis instead of Z axis")
		use_x = True

	X_SIZE = 1000
	Y_SIZE = 1000
	Z_SIZE = 1000

	OBJECT_LENGTH = 900

	SPACE = 200
	AXIS_SPACE = 20
	STEP = 5


	cnt = 0
	f = open(output_filename, "w")
	for i in range(SPACE, X_SIZE - SPACE, STEP):
		for j in range(SPACE, Y_SIZE - SPACE, STEP):
			cnt += 1
			for k in range(OBJECT_LENGTH / 2 + AXIS_SPACE, Z_SIZE - OBJECT_LENGTH / 2 - AXIS_SPACE, STEP):
				if use_x:
					f.write("%i, %i, %i\n" % (k, j, i))
				else:
					f.write("%i, %i, %i\n" % (i, j, k))

	print ("cnt = %i" % cnt)
				


if __name__ == "__main__":
	main(sys.argv)

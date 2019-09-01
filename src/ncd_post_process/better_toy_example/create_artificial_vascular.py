import os, sys
from helper import generate_grid


def main(argv):
	print ("Hello")

	if len(argv) != 3:
		print ("Usage: %s <output_file_csv> <output_file_obj>" % argv[0])
		return 1

	fname_csv = argv[1]
	fname_obj = argv[2]

	WORLD_SIZE = 1000

	VASCULAR_R = 4
	VASCULAR_D = 30

	res = []

	for i in range(VASCULAR_R, WORLD_SIZE, VASCULAR_D):
		for j in range(VASCULAR_R, WORLD_SIZE, VASCULAR_D):
			for k in range(VASCULAR_R, WORLD_SIZE, VASCULAR_R):
				res.append((i, j, k, VASCULAR_R))

	for i in range(VASCULAR_R, WORLD_SIZE, VASCULAR_D):
		for j in range(VASCULAR_R, WORLD_SIZE, VASCULAR_D):
			for k in range(VASCULAR_R, WORLD_SIZE, VASCULAR_R):
				res.append((i, k, j, VASCULAR_R))

	for i in range(VASCULAR_R, WORLD_SIZE, VASCULAR_D):
		for j in range(VASCULAR_R, WORLD_SIZE, VASCULAR_D):
			for k in range(VASCULAR_R, WORLD_SIZE, VASCULAR_R):
				res.append((k, i, j, VASCULAR_R))

	print(len(res))
	res = list(set(res))
	print(len(res))


	with open(fname_csv, "w") as f:
		for r in res:
			f.write("%i,%i,%i,%i\n" % (r[0], r[1], r[2], r[3]))

	generate_grid(0, WORLD_SIZE, VASCULAR_D, VASCULAR_R*2, fname_obj)

if __name__ == "__main__":
	main(sys.argv)

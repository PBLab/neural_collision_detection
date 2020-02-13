import os, sys
import math, random

VEC_DIFF_ANGLE_TOP = math.pi / 4
VEC_DIFF_ANGLE_BOTTOM = math.pi / 6
NEURON_R = 2
BRANCH_LENGTH_STEP_TOP = 15
BRANCH_LENGTH_STEP_BOTTOM = 16


def populate_res(res, start, vec, branch_length, vec_diff_angle, iterations):
	if iterations <= 0:
		return
	for i in range(1, branch_length + 1):
		res.append((start[0] + vec[0]*i, start[1] + vec[1]*i, start[2] + vec[2]*i, NEURON_R))
	end = (start[0] + vec[0]*branch_length, start[1] + vec[1] * branch_length, start[2] + vec[2] * branch_length)

	cos_angle = math.cos(vec_diff_angle)
	sin_angle = math.sin(vec_diff_angle)
	factor = 1.0 / math.sqrt(2)
	factor = 0.5
	x1 = vec[0] * cos_angle + vec[2] * sin_angle
	x2 = vec[0]


	y1 = vec[2] * sin_angle + vec[1] * cos_angle
	y2 = vec[1]
	z = vec[2] * cos_angle


	new_vec = (x1, y2, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)
	new_vec = (x2, y1, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)
	new_vec = (-x1, y2, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)
	new_vec = (x2, -y1, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)

	if z < 0:
		return

	new_vec = (factor*x1 + factor*y1, factor*x1 + factor*y1, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)
	new_vec = (factor*x1 + factor*y1, -factor*x1 - factor*y1, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)
	new_vec = (-factor*x1 - factor*y1, factor*x1 + factor*y1, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)
	new_vec = (-factor*x1 - factor*y1, -factor*x1 - factor*y1, z)
	populate_res(res, end, new_vec, branch_length, vec_diff_angle, iterations - 1)


def main(argv):
	print ("Hello")
	if len(argv) != 2:
		print ("Usage: %s <output_file>" % argv[0])
		return 1
	fname = argv[1]
	WORLD_X_SIZE = 500
	WORLD_Y_SIZE = 500
	WORLD_Z_SIZE = 500
	START = (0, 0, 0)
	res = []
	res.append((START[0], START[1], START[2], 8))
	vec = (0, 0, 1)
	populate_res(res, START, vec, 30, VEC_DIFF_ANGLE_TOP, 2)
	#vec = (1, 0, -0.5)
	#populate_res(res, START, vec, 30, VEC_DIFF_ANGLE_TOP, BRANCH_LENGTH_STEP_TOP)
	vec = (0, 0, -1)
	#populate_res(res, START, vec, 32, VEC_DIFF_ANGLE_BOTTOM, BRANCH_LENGTH_STEP_BOTTOM)
	#vec = (-1, 0, -0.5)
	populate_res(res, START, vec, 32, VEC_DIFF_ANGLE_BOTTOM, 2)
	#vec = (0, 1, 0)
	#populate_res(res, START, vec, BRANCH_INITIAL_LENGTH)
	#vec = (0, -1, 0)
	#populate_res(res, START, vec, BRANCH_INITIAL_LENGTH)

	print(len(res))
	res = list(set(res))
	print(len(res))


	with open(fname, "w") as f:
		for r in res:
			f.write("%f,%f,%f,%f\n" % (r[0], r[1], r[2], r[3]))


if __name__ == "__main__":
	main(sys.argv)

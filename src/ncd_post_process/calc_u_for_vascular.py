#!/state/partition1/apps/python/anaconda2/bin/python
import os, sys, time, math


def read_vascular(vascular_path):
	vascular_data = []
	idx = 0
	with open(vascular_path, "r") as f:
		for line in f:
			x, y, z, r =[float(x) for x in line.split(",")] 
			vascular_data.append([idx, x, y, z, r, 0])
			idx += 1

	return vascular_data


def distance_square(v1, v2):
	return (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2 + (v1[3] - v2[3])**2

def calc_u(vascular_data, r):
	cnt = len(vascular_data)
	ack = 0
	s = time.time()
	for i in range(cnt):
		if i % 1000 == 0:
			e = time.time()
			print("i = %i, average ack : %f, time = %i" % (i, ack*1.0 / 1000, e - s))
			s = e
			ack = 0

		for j in range(i+1, cnt):
			v1 = vascular_data[i]
			v2 = vascular_data[j]
			if v2[1] - v1[1] > r:
				#print("ack %i" % (j-i))
				ack += (j-i)
				break
			if distance_square(v1, v1) < r**2:
				vascular_data[i][-1] += 1
				vascular_data[j][-1] += 1

def sort_vascular_by_x(vascular):
	vascular.sort(key = lambda v:v[1])

def sort_vascular_by_idx(vascular):
	vascular.sort(key = lambda v:v[0])

def sort_vascular_by_u(vascular):
	vascular.sort(key = lambda v:v[-1])

def output_data(data, path):
	with open(path, "w") as f:
		for v in data:
			f.write("%i,%f,%f,%f,%f,%i\n" % (v[0], v[1], v[2], v[3], v[4], v[5]))

def main(argv):
	if len(argv) < 4:
		print("Usage: %s <vascular path> <output path> <r>" % argv[0])
		return 1

	vascular_path = argv[1]
	output_path = argv[2]
	r = float(argv[3])

	print("path: %s path: %s r: %i" % (vascular_path, output_path, r))


	vascular_data = read_vascular(vascular_path)
	print ("len: %i" % len(vascular_data))

	#vascular_data = vascular_data[:100000]

	print("Sorting...")

	sort_vascular_by_x(vascular_data)

	print("Calculating u...")

	calc_u(vascular_data, r)

	print("Sorting (again)...")

	sort_vascular_by_idx(vascular_data)

	print(vascular_data[0])

	output_data(vascular_data, output_path)

if __name__ == "__main__":
	before = time.time()
	main(sys.argv)
	after = time.time()
	print("Total time: %i seconds" % (after-before))

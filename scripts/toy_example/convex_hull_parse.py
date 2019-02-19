from chull import Vector, Hull
import sys
sys.path.append("..")
from create_cube import create_box_obj
from toy_example import parse_results_centers_bounding_box

def create_obj_file(hull, output_fname):
	vertices = []
	faces = []
	idx = 1
	for f in hull.faces:
		vertices.append(f.vertex[0])
		vertices.append(f.vertex[1])
		vertices.append(f.vertex[2])
		faces.append((idx, idx+1, idx+2))
		idx += 3

	with open(output_fname, "wb") as output_f:
		for v in vertices:
			x, y, z = v.v.x, v.v.y, v.v.z
			output_f.write("v {x} {y} {z}\n".format(**locals()))
		for f in faces:
			a1, a2, a3 = f
			output_f.write("f {a1} {a2} {a3}\n".format(**locals()))
			
		

def parse_results_centers_convex_hull(res_fname, output_fname):
	cloud = []
	with open(res_fname, "rb") as f:
		for l in f:
			els = l.split(",")
			if len(els) < 7:
				continue
			location = [int(x) for x in els[1:4]]
			#print location
			cloud.append(Vector(location[0], location[1], location[2]))

	cloud = list(set(cloud))
	print ("Computing...")
	h = Hull(cloud)
	print ("Done!")
	create_obj_file(h, output_fname)

def main(argv):
	if len(argv) < 4:
		print ("Usage: %s <input fname> <output_hull_fname> <output_box_fname>" % argv[0])
		return 1
	min_x, max_x, min_y, max_y, min_z, max_z = parse_results_centers_bounding_box(argv[1])
	create_box_obj(min_x, max_x, min_y, max_y, min_z, max_z, argv[3])
	parse_results_centers_convex_hull(argv[1], argv[2])

if __name__ == "__main__":
	main(sys.argv)

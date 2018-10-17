from utils import Utils
import numpy
import sys

class Triangulation(object):
    def __init__(self, faces_fname, vertices_fname):
        faces, num_of_faces = Utils.read_csv_file(faces_fname, int)
        faces = Utils.fix_faces(faces) # Change to 0-based arrays
        #for i, f in enumerate(faces):
            #print f
            #if i > 10:
                #break
        #sys.exit(0)

        vertices, num_of_vertices = Utils.read_csv_file(vertices_fname, float)
        print("Reading vertices ...")
        self.np_vertices = Triangulation.list_to_np_array(vertices, num_of_vertices, float)
        #Utils.memory_usage()

        print("Reading faces ...")
        self.np_faces = Triangulation.list_to_np_array(faces, num_of_faces, int)

        
        print("Num of vertices:\t", len(self.np_vertices))
        print("Num of triangles:\t", len(self.np_faces))


    @staticmethod
    def list_to_np_array(lst, lst_len, dtype=float):
        np_array = numpy.empty([lst_len, 3], dtype=dtype)
        percent = 0
        print("%2i%%" % percent + "\r",)
        sys.stdout.flush()
        for i, el in enumerate(lst):
            np_array[i, 0] = el[0]
            np_array[i, 1] = el[1]
            np_array[i, 2] = el[2]
            if (100 * i) / lst_len > percent:
                percent = (100 * i) / lst_len
                print("%2i%%" % percent + "\r")
                sys.stdout.flush()

        return np_array

    def print_stats(self):
        print("\n~~~   STATS   ~~~\n")
        print("Num of vertices:\t", len(self.np_vertices))
        print("Num of triangles:\t", len(self.np_faces))
        print("\n===\tVertices\t===")
        print(self.np_vertices)
        Utils.get_min_max(self.np_vertices)

        print("\n===\tFaces\t===")
        print(self.np_faces)
        Utils.get_min_max(self.np_faces)

    def get_obj_creator(self):
        creator = ObjCreator(self.np_vertices, self.np_faces, len(self.np_vertices), len(self.np_faces)) # TODO: remove len
        return creator

class ObjCreator:
    def __init__(self, np_verts, np_triangles, num_of_vertices, num_of_triangles):
        self.np_verts = np_verts
        self.np_triangles = np_triangles
        self.num_of_vertices = num_of_vertices
        self.num_of_triangles = num_of_triangles

    
    def write_vertex(self, v):
        s  = ""
        #s += "vn 0.0 0.0 1.0\n"
        s += "v %f %f %f\n" % (v[0], v[1], v[2])
        self.out_file.write(s)

    def write_triangle(self, t):
        s = "f %i %i %i\n" % (t[0]+1,
                                          t[1]+1,
                                          t[2]+1)
        #s = "f %i//%i %i//%i %i//%i\n" % (t[0]+1, t[0]+1,
                                          #t[1]+1, t[1]+1,
                                          #t[2]+1, t[2]+1)

        self.out_file.write(s)

    def create_obj_file(self, fname):
        self.out_file = open(fname, "w")
        for v in self.np_verts:
            self.write_vertex(v)

        for t in self.np_triangles:
            self.write_triangle(t)

import bpy
import numpy as np


def add_spheres(fname):
    """ Add each point in the array as a sphere """
    data = np.loadtxt(fname, dtype=np.uint32)
    assert data.shape[0] == 4

    for x, y, z, r in zip(data[0], data[1], data[2], data[3]):
        _ = bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius=r/30,
                                                               location=(x, y, z))


if __name__ == '__main__':
    fname = r'C:\Users\Hagai\Downloads\arr.csv'
    add_spheres(fname)
import sys

import numpy as np
import numba

from helper import generate_grid


def parse_inp(argv):
    print("Hello")
    if len(argv) != 4:
        print("Usage: %s <output_file_csv> <output_file_obj> <grid_size>" % argv[0])
        return 1
    fname_csv = argv[1]
    fname_obj = argv[2]
    WORLD_SIZE = 1000
    VASCULAR_D = int(argv[3])
    VASCULAR_R = VASCULAR_D // 2
    return fname_csv, fname_obj, WORLD_SIZE, VASCULAR_D, VASCULAR_R


def cartesian(*arrays):
    mesh = np.meshgrid(*arrays)  # standard numpy meshgrid
    dim = len(mesh)  # number of dimensions
    elements = mesh[0].size  # number of elements, any index will do
    flat = np.concatenate(mesh).ravel()  # flatten the whole meshgrid
    reshape = np.reshape(flat, (dim, elements)).T  # reshape and transpose
    return reshape


def main(fname_csv, fname_obj, WORLD_SIZE, VASCULAR_D, VASCULAR_R):
    xs = np.arange(VASCULAR_R, WORLD_SIZE, VASCULAR_D)
    ys = np.arange(VASCULAR_R, WORLD_SIZE, VASCULAR_D)
    zs = np.arange(VASCULAR_R, WORLD_SIZE, VASCULAR_R)
    res = cartesian(xs, ys, zs, [VASCULAR_R])
    res2 = res.copy()
    res2[:, 1] = res[:, 2]
    res2[:, 2] = res[:, 1]

    res3 = res.copy()
    res3[:, 0] = res[:, 2]
    res3[:, 1] = res[:, 0]
    res3[:, 2] = res[:, 1]

    res = np.unique(np.vstack((res, res2, res3)), axis=0)

    print(len(res))
    return res


def write_to_disk(res):
    np.savetxt(fname_csv, res, delimiter=',', fmt='%d')
    # with open(fname_csv, "w") as f:
    #     for r in res:
    #         f.write(b"%i,%i,%i,%i\n" % (r[0], r[1], r[2], r[3]))
    generate_grid(0, WORLD_SIZE, VASCULAR_D, VASCULAR_R * 2, fname_obj)


if __name__ == "__main__":
    diameters = [1, 3, 5, 7, 10, 13, 15, 17, 20]
    fname_csv, fname_obj, WORLD_SIZE, VASCULAR_D, VASCULAR_R = parse_inp(sys.argv)
    res = main(fname_csv, fname_obj, WORLD_SIZE, VASCULAR_D, VASCULAR_R)
    write_to_disk(res)

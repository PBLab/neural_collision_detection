import numpy as np
import DrawingXtras
from mytools import *
from collections import namedtuple
import bpy

Coor = namedtuple("Coor", ("x", "y", "z"))


def gen_bins(colls: np.ndarray, l: Coor):
    max_x, min_x = np.max(colls[:, 0]), np.min(colls[:, 0])
    max_y, min_y = np.max(colls[:, 1]), np.min(colls[:, 1])
    max_z, min_z = np.max(colls[:, 2]), np.min(colls[:, 2])
    bins_x = int(np.ceil(max_x - min_x / l.x))
    bins_y = int(np.ceil(max_y - min_y / l.y))
    bins_z = int(np.ceil(max_z - min_z / l.z))
    hist, edges = np.histogramdd(colls, bins=(bins_x, bins_y, bins_z))
    return hist, edges


def draw_collisions(colls, hist, edges):
    norm = 1.0 / np.max(hist)
    relevant_coords = np.where(
        hist > 0
    )  # each row is a dimension, each column a coordinate
    num_dims = 3
    num_ones = len(relevant_coords[0])
    bin_starts = np.zeros((num_ones, num_dims))
    bin_ends = np.zeros_like(bin_starts)
    assert len(edges) == len(relevant_coords)
    for coor_idx, (coor, edge) in enumerate(zip(relevant_coords, edges)):
        bin_starts[:, coor_idx] = edge[coor]
        bin_ends[:, coor_idx] = edge[coor + 1]

    return hist[relevant_coords], bin_starts, bin_ends


def create_verts_faces_and_draw(hist, bin_starts, bin_ends):
    OPS_LAYER = 0
    norm = 1.0 / hist.max()
    for val, coll_start, coll_end in zip(hist, bin_starts, bin_ends):
        voxel_verts = [
            [*coll_start],
            [coll_end[0], *coll_start[1:]],
            [coll_start[0], coll_end[1], coll_start[2]],
            [*coll_end[:2], coll_start[2]],
            [*coll_start[:2], coll_end[2]],
            [coll_end[0], coll_start[1], coll_end[2]],
            [coll_start[0], *coll_end[1:]],
            [*coll_end],
        ]
        voxel_faces = [
            [0, 1, 3, 2],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 3, 7, 5],
            [3, 2, 6, 7],
            [2, 0, 4, 6],
        ]
        # Draw
        # ----------------------------------------------------
        name = "collisions"
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.objects.link(obj)
        mesh.from_pydata(voxel_verts, [], voxel_faces)
        mesh.update(calc_edges=True)
        # apply material
        mat = bpy.data.materials.new(name + "_Mat")
        mat.diffuse_color = [val * norm, 0.0, 0.0]
        mat.diffuse_shader = "LAMBERT"
        mat.diffuse_intensity = 1.0
        mat.specular_color = [0.0, 0.0, 0.0]
        mat.specular_shader = "COOKTORR"
        mat.specular_intensity = 1.0
        mat.alpha = val * norm * 0.5
        mat.ambient = 1.0
        # mat.transparency_method = 'Z_TRANSPARENCY'
        obj.data.materials.append(mat)

        # set layers
        layers = [False] * 20
        layers[(bpy.context.scene["MyDrawTools_BaseLayer"] + OPS_LAYER) % 20] = True
        obj.layers = layers


def get_border_box(neuron, l):
    """
    Returns three 3D objects:
    bins: the number of bins in each dimension for a given neuron,
    normalized to a l.x-by-l.y-by-l.z box in um.
    maxp: Maximal coordinate of the neuron in all three dimensions.
    minp: Minimal coordinate of the neuron in all three dimensions.
    Assumes that at least a single neuron was already loaded, and that
    mytools was imported.
    Taken directly from Py3DN with very minor changes by Hagai Har-Gil.
    """

    # to make things more readable
    X = 0
    Y = 1
    Z = 2

    # Find out how many coordinates the neuron contains
    num_of_dims = 3
    num_of_points = 0
    for tree in neuron.tree:
        num_of_points += len(tree.rawpoint)
    neuron_coords = np.zeros((num_of_points, num_of_dims))

    row = 0
    for tree in neuron.tree:
        for point in tree.rawpoint:
            neuron_coords[row, :] = point.P
            row += 1

    min_point = neuron_coords.min(axis=0)
    max_point = neuron_coords.max(axis=0)

    bins_x = int((max_point[X] - min_point[X]) / l.x) + 2
    bins_y = int((max_point[Y] - min_point[Y]) / l.y) + 2
    bins_z = int((max_point[Z] - min_point[Z]) / l.z) + 2

    bins = Coor(bins_x, bins_y, bins_z)
    maxp = Coor(max_point[X], max_point[Y], max_point[Z])
    minp = Coor(min_point[X], min_point[Y], min_point[Z])

    return bins, maxp, minp


if __name__ == "__main__":
    # Should only be run under Blender
    l = Coor(5, 5, 5)  # in um
    fname = r"/mnt/qnap/simulated_morph_data/results/2019_1_2/collisions.npz"
    downsample_factor = 10_000
    collisions = np.load(fname)["translated"][::downsample_factor, :]
    hist, edges = gen_bins(collisions, l)
    nonzero_hist, bin_starts, bin_ends = draw_collisions(collisions, hist, edges)
    create_verts_faces_and_draw(nonzero_hist, bin_starts, bin_ends)
    print("Done!")

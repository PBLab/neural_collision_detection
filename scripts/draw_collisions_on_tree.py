""" Should only be run under Blender """
import numpy as np
import scipy.spatial.distance
import DrawingXtras
from mytools import *
from collections import namedtuple
import bpy

from overlay_collisions import gen_bins, Coor


def draw_tree_collisions(tree, object_name, collisions_hist, bin_starts, bin_ends):

    collisions_on_tree = np.zeros(tree.total_points)
    colorcodes = np.zeros((tree.total_points, 3))
    N = bpy.context.scene.MyDrawTools_TreesDetail

    min_collision_num = 0
    max_collisions_num = collisions_hist.max()

    bin_centers = (bin_starts + bin_ends) / 2
    points_on_tree = np.zeros((tree.total_points, 3))
    for idx, point in enumerate(tree.point):
        points_on_tree[idx, :] = point.P

    # The columns of the following arrays represent the bins, and the rows represent
    # the number of points on the tree
    point_to_bin_distance = scipy.spatial.distance.cdist(points_on_tree, bin_centers)
    closest_bin_per_point = point_to_bin_distance.argmin(axis=1)
    assert len(bin_centers) == len(collisions_hist)
    collision_value_on_point = collisions_hist[closest_bin_per_point] / max_collisions_num
    colorcodes[:, 0] = collision_value_on_point
    colorcodes[:, 2] = 1 - collision_value_on_point

    # Now create a mesh with color information for each vertice
    my_object = bpy.data.objects[object_name].data
    color_map_collection = my_object.vertex_colors
    if len(color_map_collection) == 0:
        color_map_collection.new()
    color_map = color_map_collection['Col'] #let us assume for sake of brevity that there is now a vertex color map called  'Col'
    # or you could avoid using the vertex color map name
    # color_map = color_map_collection.active

    for pid in range(tree.total_points-1):
        for i in range(N):
            color_map.data[pid*N+i].color = [ colorcodes[pid, 0], colorcodes[pid, 1], colorcodes[pid, 2] ]

    mate = bpy.data.materials.new('vertex_material')
    mate.use_vertex_color_paint = True
    mate.use_vertex_color_light = True  # material affected by lights
    my_object.materials.append(mate)

    # set to vertex paint mode to see the result
    bpy.ops.object.mode_set(mode='VERTEX_PAINT')
    print(f'\nCollision Map:\n\tpure blue is 0 collisions;\n\tpure red is {max_collisions_num} collisions')


def filter_relevant_bins(colls, hist, edges):
    """
    After generating the histogram of collisions, filters out only
    the bins in which a collisions occurred. It then generates two
    arrays which contain the start and end of the bins containing the
    collisions in microns.
    """
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


if __name__ == "__main__":
    l = Coor(5, 5, 5)  # in um
    fname = r"/mnt/qnap/simulated_morph_data/results/2019_1_2/collisions_nparser.npz"
    downsample_factor = 1000
    collisions = np.load(fname)["translated"][::downsample_factor, :]
    hist, edges = gen_bins(collisions, l)
    nonzero_hist, bin_starts, bin_ends = filter_relevant_bins(collisions, hist, edges)
    draw_tree_collisions(mytools.neuron[0].tree[0], 'Axon', nonzero_hist, bin_starts, bin_ends)

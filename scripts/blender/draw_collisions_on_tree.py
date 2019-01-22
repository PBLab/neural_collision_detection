""" Should only be run under Blender """
from collections import namedtuple
import pathlib
import numpy as np
import scipy.spatial.distance
import DrawingXtras
from mytools import *
import bpy
import attr
from attr.validators import instance_of

from overlay_collisions import gen_bins, Coor, filter_relevant_bins


@attr.s
class CollisionDrawer:
    """ Draws on a loaded Blender neuron the normalized number
    of collisions it 'felt'.

    Assumes that neuron[0] is a loaded Blender neuron
    (``from mytools import *``) """

    fname = attr.ib(validator=instance_of(pathlib.Path))
    binsize = attr.ib(default=(5, 5, 5), validator=instance_of(tuple))
    downsample = attr.ib(default=1000, validator=instance_of(int))
    npz_keyname = attr.ib(default="translated", validator=instance_of(str))
    total_points = attr.ib(init=False)
    colorcodes = attr.ib(init=False)
    points_on_neuron = attr.ib(init=False)
    collisions = attr.ib(init=False)

    def __attrs_post_init__(self):
        assert neuron[0]
        self.total_points = 0
        for tree in neuron[0].tree:
            self.total_points += tree.total_points

    def run(self):
        """
        Main class pipeline.

        Histograms the collisions into bins with the same shape as the neuron, and
        then filters out the empty ones. It then takes this non-zero histogram and
        compares the collision locations with the neuron's actual data points to
        "color" each neuronal segment with a color proportionate to the number of
        collisions in that area.
         """
        self.collisions = np.load(fname)[self.npz_keyname][::self.downsample, :]
        hist, edges = gen_bins(self.collisions, self.binsize)
        nonzero_hist, bin_starts, bin_ends = filter_relevant_bins(self.collisions, hist, edges)
        self.points_on_neuron = self._get_all_points_into_array()

        draw_tree_collisions(neuron[0], "Axon", nonzero_hist, bin_starts, bin_ends)

    def _get_all_points_into_array(self) -> np.ndarray:
        """ For faster processing, loads all neural coordinates
        into a numpy array, where each line is a coordinate with
        three (x, y, z) values """
        points_on_neuron = np.zeros((self.total_points, 3))
        for tree in neuron[0].tree:
            for idx, point in enumerate(tree.rawpoint):
                points_on_neuron[idx, :] = point.P
        return points_on_neuron

    def _


def draw_tree_collisions(tree, object_name, collisions_hist, bin_starts, bin_ends):

    colorcodes = np.zeros((tree.total_points, 3))
    N = bpy.context.scene.MyDrawTools_TreesDetail

    max_collisions_num = collisions_hist.max()

    bin_centers = (bin_starts + bin_ends) / 2

    # The columns of the following arrays represent the bins, and the rows represent
    # the number of points on the tree
    point_to_bin_distance = scipy.spatial.distance.cdist(points_on_tree, bin_centers)
    closest_bin_per_point = point_to_bin_distance.argmin(axis=1)
    assert len(bin_centers) == len(collisions_hist)
    collision_value_on_point = (
        collisions_hist[closest_bin_per_point] / max_collisions_num
    )
    colorcodes[:, 0] = collision_value_on_point
    colorcodes[:, 2] = 1 - collision_value_on_point

    # Now create a mesh with color information for each vertice
    my_object = bpy.data.objects[object_name].data
    color_map_collection = my_object.vertex_colors
    if len(color_map_collection) == 0:
        color_map_collection.new()
    color_map = color_map_collection[
        "Col"
    ]  # let us assume for sake of brevity that there is now a vertex color map called  'Col'
    # or you could avoid using the vertex color map name
    # color_map = color_map_collection.active

    for pid in range(tree.total_points - 1):
        for i in range(N):
            color_map.data[pid * N + i].color = [
                colorcodes[pid, 0],
                colorcodes[pid, 1],
                colorcodes[pid, 2],
            ]

    mate = bpy.data.materials.new("vertex_material")
    mate.use_vertex_color_paint = True
    mate.use_vertex_color_light = True  # material affected by lights
    my_object.materials.append(mate)

    # set to vertex paint mode to see the result
    bpy.ops.object.mode_set(mode="VERTEX_PAINT")
    print(
        f"\nCollision Map:\n\tpure blue is 0 collisions;\n\tpure red is {max_collisions_num} collisions"
    )


if __name__ == "__main__":
    fname = r"/mnt/qnap/simulated_morph_data/results/2019_1_2/collisions_nparser.npz"
    downsample_factor = 1000
    binsize = (5, 5, 5)
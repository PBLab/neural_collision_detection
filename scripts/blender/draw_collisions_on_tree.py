""" Should only be run under Blender """
from collections import namedtuple
from typing import Tuple
from importlib import reload
import pathlib
import sys

import numpy as np
import pandas as pd
import scipy.spatial.distance
import DrawingXtras
from mytools import *
import bpy
import attr
from attr.validators import instance_of

sys.path.append(
    "/mnt/qnap/simulated_morph_data/neural_collision_detection/scripts/blender"
)
from overlay_collisions import gen_bins, filter_relevant_bins
import general_methods

from mytools import *


@attr.s
class CollisionDrawer:
    """ Draws on a loaded Blender neuron the normalized number
    of collisions it 'felt'.

    Assumes that neuron[0] is a loaded Blender neuron
    (``from mytools import *``) and that we're in "Vertex Pain" mode. """

    fname = attr.ib(validator=instance_of(pathlib.Path))
    binsize = attr.ib(default=(5, 5, 5), validator=instance_of(tuple))
    downsample = attr.ib(default=1000, validator=instance_of(int))
    npz_keyname = attr.ib(default="neuron_coords", validator=instance_of(str))
    collisions_fname = attr.ib(default=None)
    total_points = attr.ib(init=False)
    tree_names = attr.ib(init=False)
    points_on_neuron = attr.ib(init=False)
    collisions = attr.ib(init=False)

    def __attrs_post_init__(self):
        assert neuron[0]
        self.total_points = 0
        for tree in neuron[0].tree:
            self.total_points += tree.total_rawpoints

    def run(self):
        """
        Main class pipeline.

        Histograms the collisions into bins with the same shape as the neuron, and
        then filters out the empty ones. It then takes this non-zero histogram and
        compares the collision locations with the neuron's actual data points to
        "color" each neuronal segment with a color proportionate to the number of
        collisions in that area.
         """
        self.collisions = np.load(fname)[self.npz_keyname][:: self.downsample, :]
        self.tree_names = general_methods.name_neuron_trees(neuron[0])
        hist, edges = gen_bins(self.collisions, self.binsize)
        nonzero_hist, bin_starts, bin_ends = filter_relevant_bins(
            self.collisions, hist, edges
        )
        self.points_on_neuron = self._get_all_points_into_array()
        closest_bin_per_point = self._find_distance_between_neuron_and_collision(
            nonzero_hist, bin_starts, bin_ends
        )
        colorcodes, collisions_per_neuron_point = self._generate_color_codes(nonzero_hist, closest_bin_per_point)
        self._redraw_trees(colorcodes)
        if self.collisions_fname:
            self._serialize_collisions_per_neuron_points(collisions_per_neuron_point)

    def _get_all_points_into_array(self) -> np.ndarray:
        """ For faster processing, loads all neural coordinates
        into a pandas dataframe, where each line is a coordinate with
        three (x, y, z) values. The index of the frame is the
        type of tree is was taken from. """
        points_on_neuron = np.zeros((self.total_points, 3))
        object_name = np.zeros((self.total_points,), dtype=object)
        starting_idx = 0
        for name, tree in zip(self.tree_names, neuron[0].tree):
            for idx, point in enumerate(tree.rawpoint, starting_idx):
                points_on_neuron[idx, :] = point.P
                object_name[idx] = name
            starting_idx = idx + 1
        object_name = pd.CategoricalIndex(object_name)
        numerical_index = np.arange(len(object_name))
        return pd.DataFrame(
            {
                "x": points_on_neuron[:, 0],
                "y": points_on_neuron[:, 1],
                "z": points_on_neuron[:, 2],
            },
            index=pd.MultiIndex.from_arrays([numerical_index, object_name]),
        )

    def _find_distance_between_neuron_and_collision(
        self, collisions_hist, bin_starts, bin_ends
    ) -> np.ndarray:
        """
        Returns the closest histogram bin to a coordinate on the neuron.

        For the given histogram edges (bin_starts, bin_ends) computes the distance
        matrix between the neuron and the bins. The rows are the coordinates of
        the points on the neuron, and the columns are the coordinates of the
        bin edges. In the resulting 2D matrix, the cell at location (m, n) contains the
        distance between the m-th point on the neuron and the n-th bin that contained a
        collision. The function returns the minimum of these columns, i.e. the closest
        histogram bin per neural coordinate.
        """
        bin_centers = (bin_starts + bin_ends) / 2
        point_to_bin_distance = scipy.spatial.distance.cdist(
            self.points_on_neuron.values, bin_centers
        )
        closest_bin_per_point = point_to_bin_distance.argmin(axis=1)
        return closest_bin_per_point

    def _generate_color_codes(self, collisions_hist, closest_bin_per_point):
        """
        Decide on the color value of each point in the neuron. This
        values is proportionate to the number of collisions on that point.
        """
        colorcodes = np.zeros_like(self.points_on_neuron)
        max_collisions_num = collisions_hist.max()
        collision_value_on_point = (
            collisions_hist[closest_bin_per_point] / max_collisions_num
        )

        colorcodes[:, 0] = collision_value_on_point
        colorcodes[:, 2] = 1 - collision_value_on_point
        return colorcodes, collisions_hist[closest_bin_per_point]

    def _redraw_trees(self, colorcodes):
        """
        Using the given color codes, traverse every point on every neuronal
        tree and color it
        FIXME - the colorcodes row index keeps repeating itself
        """
        # aaaaaa NOT WORKING PROPERLY DON'T USE AAAAAAAA
        detail_level = bpy.context.scene.MyDrawTools_TreesDetail
        for object_name, tree in zip(self.tree_names, neuron[0].tree):
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
            cur_tree = self.points_on_neuron.xs(object_name, level=1)
            for idx, (pid, _) in enumerate(cur_tree.iterrows()):
                for i in range(detail_level):
                    color_map.data[idx * detail_level + i].color = [
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

    def _serialize_collisions_per_neuron_points(self, data):
        """ Writes the array containing the number of collisions
        per neuronal point to disk """
        np.save(self.collisions_fname, data)


if __name__ == "__main__":
    general_methods = reload(general_methods)
    fname = pathlib.Path(
        r"/mnt/qnap/simulated_morph_data/results/2019_2_10/normalized_agg_results_AP120410_s1c1_thresh_0.npz"
    )
    downsample_factor = 1000
    binsize = (5, 5, 5)
    colls_fname = "/home/hagaihargil/Downloads/colls.npy"
    coll_drawer = CollisionDrawer(
        fname=fname,
        downsample=downsample_factor,
        binsize=binsize,
        collisions_fname=colls_fname,
    )
    coll_drawer.run()

""" Should only be run under Blender """
from collections import namedtuple
import pathlib
import numpy as np
import pandas as pd
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
    (``from mytools import *``) and that we're in "Vertex Pain" mode. """

    fname = attr.ib(validator=instance_of(pathlib.Path))
    binsize = attr.ib(default=(5, 5, 5), validator=instance_of(tuple))
    downsample = attr.ib(default=1000, validator=instance_of(int))
    npz_keyname = attr.ib(default="translated", validator=instance_of(str))
    total_points = attr.ib(init=False)
    tree_names = attr.ib(init=False)
    points_on_neuron = attr.ib(init=False)
    collisions = attr.ib(init=False)

    def __attrs_post_init__(self):
        assert neuron[0]
        self.total_points = 0
        for tree in neuron[0].tree:
            self.total_points += tree.total_points

    def _name_neuron_trees(self):
        """ Find the names Blender uses for the axon and dendrites """
        basic_tree_names = []
        for tree in neuron[0].tree:
            basic_tree_names.append(tree.type)
        real_tree_names = []
        idx_axon = 1
        idx_dendrite = 1
        for treename in basic_tree_names:
            if treename not in self.tree_names:
                real_tree_names.append(tree)
                continue
            if 'Axon' == treename:
                new_name = f'Axon.00{idx_axon}'
                idx_axon += 1
            elif 'Dendrite' == treename:
                new_name = f'Dendrite.00{idx_dendrite}'
                idx_dendrite += 1
            real_tree_names.append(new_name)
        return real_tree_names

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
        self.tree_names = self._name_neuron_trees()
        hist, edges = gen_bins(self.collisions, self.binsize)
        nonzero_hist, bin_starts, bin_ends = filter_relevant_bins(self.collisions, hist, edges)
        self.points_on_neuron = self._get_all_points_into_array()
        closest_bin_per_point = self._find_distance_between_neuron_and_collision(nonzero_hist, bin_starts, bin_ends)
        colorcodes = self._generate_color_codes(nonzero_hist, closest_bin_per_point)
        self._redraw_trees(colorcodes)

    def _get_all_points_into_array(self) -> np.ndarray:
        """ For faster processing, loads all neural coordinates
        into a pandas dataframe, where each line is a coordinate with
        three (x, y, z) values. The index of the frame is the
        type of tree is was taken from. """
        points_on_neuron = np.zeros((self.total_points, 3))
        object_name = np.zeros((self.total_points,), dtype=object)
        for name, tree in zip(self.tree_names, neuron[0].tree):
            for idx, point in enumerate(tree.rawpoint):
                points_on_neuron[idx, :] = point.P
                object_name[idx, :] = name
        object_name = pd.CategoricalIndex(object_name)
        numerical_index = np.arange(len(object_name))
        return pd.DataFrame({'coor': points_on_neuron},
                            index=pd.MultiIndex.from_arrays([numerical_index, object_name]))

    def _find_distance_between_neuron_and_collision(self, collisions_hist, bin_starts, bin_ends) -> np.ndarray:
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
        point_to_bin_distance = scipy.spatial.distance.cdist(self.points_on_neuron, bin_centers)
        closest_bin_per_point = point_to_bin_distance.argmin(axis=1)
        assert len(bin_centers) == len(collisions_hist)
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
        return colorcodes

    def _redraw_trees(self, colorcodes):
        """
        Using the given color codes, traverse every point on every neuronal
        tree and color it
        """
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
            for pid, _ in cur_tree.iterrows():
                for i in range(detail_level):
                    color_map.data[pid * detail_level + i].color = [
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


if __name__ == "__main__":
    fname = r"/mnt/qnap/simulated_morph_data/results/2019_1_2/collisions_nparser.npz"
    downsample_factor = 1000
    binsize = (5, 5, 5)
    coll_drawer = CollisionDrawer(fname=fname, downsample=downsample_factor, binsize=binsize)
    coll_drawer.run()
    
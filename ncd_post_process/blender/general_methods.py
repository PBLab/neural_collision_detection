"""
Assortment of functions that are usually called
whenever we deal with visualization in Blender.
"""
import numpy as np
import pandas as pd
import attr
from attr.validators import instance_of

# import bpy

# from mytools import *


@attr.s(frozen=True)
class TreeLimits:
    """
    Simple dataclass that holds the starting and ending index for
    each tree name in a given dataframe. Sould be used for the function
    redraw_trees below.
    """

    limits = attr.ib(validator=instance_of(list))

    @classmethod
    def from_hiddenness_df(cls, df):
        """
        Constructs these tree limits from a DataFrame generated in the
        "find_branching_density" script
        """
        names = df.index.levels[1].values
        limits = []
        for name in names:
            current = df.xs(name, level=1)
            min_idx = current.index.get_level_values(0).min()
            max_idx = current.index.get_level_values(0).max()
            limits.append((name, min_idx, max_idx + 1))
        return TreeLimits(limits)


def name_neuron_trees(inp_neuron=None):
    """ Find the names Blender uses for the axon and dendrites """
    if inp_neuron:
        neuron = inp_neuron
    else:
        neuron = neuron[0]
    basic_tree_names = []
    for tree in neuron.tree:
        basic_tree_names.append(tree.type)
    real_tree_names = []
    idx_axon = 1
    idx_dendrite = 1
    for treename in basic_tree_names:
        if treename not in real_tree_names:
            real_tree_names.append(treename)
            continue
        if "Axon" == treename:
            new_name = f"Axon.00{idx_axon}"
            idx_axon += 1
        elif "Dendrite" == treename:
            new_name = f"Dendrite.00{idx_dendrite}"
            idx_dendrite += 1
        real_tree_names.append(new_name)
    return real_tree_names


def generate_color_codes(data):
    """
    Decide on the color value of each point in the neuron. This
    values is proportionate to the value of data in that point.
    """
    colorcodes = np.zeros((data.shape[0], 3))
    normed_data = (data / data.max()).ravel()
    colorcodes[:, 0] = normed_data
    colorcodes[:, 2] = 1 - normed_data
    print(f"Normed data mean {normed_data.mean()}")
    return colorcodes


def redraw_trees(colorcodes: np.ndarray, limits: TreeLimits):
    """
    Under Blender, using the given color codes, traverse every point on every neuronal
    tree and color it. Assumes being run under Blender and that a variable "neuron" is in scope.
    """
    detail_level = bpy.context.scene.MyDrawTools_TreesDetail
    for name, start_idx, end_idx in limits.limits:
        my_object = bpy.data.objects[name].data
        color_map_collection = my_object.vertex_colors
        if len(color_map_collection) == 0:
            color_map_collection.new()
        # color_map = color_map_collection[
        #     "Col"
        # ]  # let us assume for sake of brevity that there is now a vertex color map called  'Col'
        # or you could avoid using the vertex color map name
        color_map = color_map_collection.active
        for cur_idx, pid in enumerate(range(start_idx, end_idx)):
            for i in range(detail_level):
                color_map.data[cur_idx * detail_level + 1].color = [
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

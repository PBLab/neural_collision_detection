# Should be run under Blender
from mytools import *
import numpy as np
import networkx as nx


def make_neuron_aware_collision_df(collisions, neuron):
    """
    Traverses the neuronal tree and the corresponding
    collisions and assigns an index for each collision number
    that corresponds to the neuronal location and information
    of that spot.

    The indices are the
    :param np.ndarray collisions: All measured collisions of
    the neuron, including the zeros.
    :param Neuron neuron: A serialized neuron from py3DN.
    """
    num_of_nodes = 0
    for tree in neuron.tree:
        num_of_nodes += tree.total_points
    assert num_of_nodes == collisions.shape[0]
    





def correlate_collisions_with_distance(collisions, neuron):
    """
    Traverses the neuronal tree and bins the number of collisions
    on each given neurnal point per its topological distance from
    the cell body.
    """
    total_points = collisions.shape[0]
    neuron_total_points = 0
    for tree in neuron.tree:
        neuron_total_points += tree.total_points
    assert total_points == neuron_total_points







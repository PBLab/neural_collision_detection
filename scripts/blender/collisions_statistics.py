import enum

from py3DN.mytools import Get_FiberDistance_Between_RawPoints
import numpy as np
import networkx as nx
import attr
import pandas as pd
from attr.validators import instance_of


class PointType(enum.Enum):
    STANDARD = 'standard'
    NODE = 'node'
    ENDPOINT = 'endpoint'


@attr.s(frozen=True)
class CollisionNode:
    """
    A single node on a neuronal tree.

    :param np.ndarray loc: a 3-sized vector with coordinates.
    :param int ppid: parent point ID.
    :param PointType ptype:
    :param int collisions: Number of collisions on the node.
    """
    loc = attr.ib(validator=instance_of(np.ndarray))
    ppid = attr.ib(validator=instance_of(int))
    ptype = attr.ib(validator=instance_of(PointType))
    collisions = attr.ib(validator=instance_of(int))


def make_collision_df(collisions, neuron):
    """
    Traverses the neuronal tree and the corresponding
    collisions and generates a DF that will be transformed
    into a graph, with its nodes being the metadata of that
    point on the neuronal tree (the CollisionNode class).
    Edge weight in this graph is the topological distance
    between the two points.

    :param np.ndarray collisions: All measured collisions of
    the neuron, including the zeros.
    :param Neuron neuron: A serialized neuron from py3DN.
    """
    num_of_nodes = 0
    for tree in neuron.tree:
        num_of_nodes += tree.total_points
    assert num_of_nodes == collisions.shape[0]

    df = pd.DataFrame({'a': np.zeros(num_of_nodes, dtype=object),
                       'b': np.zeros(num_of_nodes, dtype=object),
                       'distance': np.zeros(num_of_nodes)})
    pid_idx = 0
    for tree in neuron.tree:
        parent_node = CollisionNode(
            loc=np.array(tree.point[0].P),
            ppid=-1,
            ptype=PointType.STANDARD,
            collisions=collisions[pid_idx],
        )

        pid_idx += 1
        for point in tree.point[1:]:
            CollisionNode
            pid_idx += 1









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







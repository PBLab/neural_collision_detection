import enum
import pathlib
import sys
import contextlib

import numpy as np
import networkx as nx
import attr
import pandas as pd
from attr.validators import instance_of
import scipy.spatial.distance



class PointType(enum.Enum):
    STANDARD = "standard"
    NODE = "node"
    ENDPOINT = "endpoint"

    @classmethod
    def from_str(cls, inp_str):
        if inp_str == "standard":
            return cls.STANDARD
        elif inp_str == "node":
            return cls.NODE
        elif inp_str == "endpoint":
            return cls.ENDPOINT
        raise ValueError


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
    radius = attr.ib(validator=instance_of(float))


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
        num_of_nodes += tree.total_rawpoints
    assert num_of_nodes == collisions.shape[0]

    df = pd.DataFrame(
        {
            "from": np.zeros(num_of_nodes, dtype=object),
            "to": np.zeros(num_of_nodes, dtype=object),
            "distance": np.zeros(num_of_nodes),
        }
    )
    pid_idx = 0
    for tree in neuron.tree:
        parent_node = CollisionNode(
            loc=np.array(tree.rawpoint[0].P),
            ppid=-1,
            ptype=PointType.STANDARD,
            collisions=collisions[pid_idx],
            radius=tree.rawpoint[0].r,
        )
        new_node = CollisionNode(
            loc=np.array(tree.rawpoint[1].P),
            ppid=tree.rawpoint[1].ppid,
            ptype=tree.rawpoint[1].pytpe,
            collisions=collisions[1],
            radius=tree.rawpoint[1].r,
        )
        dist = scipy.spatial.distance.pdist([tree.rawpoint[0].P, tree.rawpoint[1].P])
        df.iloc[pid_idx] = [parent_node, new_node, dist]
        pid_idx += 1
        for point in tree.rawpoint[2:]:
            prev_node = new_node
            del new_node
            new_node = CollisionNode(
                loc=np.array(point.P),
                ppid=point.ppid,
                ptype=PointType.from_str(point.ptype),
                collisions=collisions[pid_idx],
                radius=point.r,
            )
            dist = scipy.spatial.distance.pdist([prev_node.loc, np.array(point.P)])
            df.iloc[pid_idx] = [prev_node, new_node, dist]
            pid_idx += 1
    return df


def correlate_collisions_with_distance(collisions, neuron):
    """
    Traverses the neuronal tree and bins the number of collisions
    on each given neurnal point per its topological distance from
    the cell body.
    """
    total_points = collisions.shape[0]
    neuron_total_points = 0
    for tree in neuron.tree:
        neuron_total_points += tree.total_rawpoints
    assert total_points == neuron_total_points


@contextlib.contextmanager
def load_neuron(fname):
    """
    Uses py3DN's Load_Neuron function to load an XML representation
    of a NeuroLucida neuron into memory.
    Uses a context manager since it mingles with sys.path, and
    we wish to leave it unchanged at the end of the execution.
    """
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[3] / 'py3DN'))
    import NeuroLucidaXMLParser
    neuron = NeuroLucidaXMLParser.Load_Neuron(fname, 0.17, False)
    try:
        yield neuron
    finally:
        sys.path.pop(-1)


if __name__ == "__main__":
    neuron_fname = '/data/simulated_morph_data/neurons/AP120410_s1c1.xml'
    collisions_fname = '/data/simulated_morph_data/results/2019_2_10/normalized_agg_AP120410_s1c1_thresh_0.npz'
    collisions = np.load(collisions_fname)
    with load_neuron(neuron_fname) as neuron:
        df = make_collision_df(collisions['neuron_coords'], neuron)

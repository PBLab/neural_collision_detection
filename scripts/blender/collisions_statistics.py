import enum
import pathlib
import sys
import contextlib
import multiprocessing as mp
import functools

import numpy as np
import networkx as nx
import attr
import pandas as pd
from attr.validators import instance_of
import scipy.spatial.distance


sys.path.append(str(pathlib.Path(__file__).resolve().parents[3] / "py3DN"))
import mytools


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


class TreeType(enum.Enum):
    AXON = "Axon"
    DENDRITE = "Dendrite"

    @classmethod
    def from_str(cls, inp_str):
        if inp_str == "Axon":
            return cls.AXON
        if inp_str == "Dendrite":
            return cls.DENDRITE


@attr.s(frozen=True)
class CollisionNode:
    """
    A single node on a neuronal tree.

    :param np.ndarray loc: a 3-sized vector with coordinates.
    :param int ppid: parent point ID.
    :param PointType ptype:
    :param int collisions: Number of collisions on the node.
    """

    loc = attr.ib(validator=instance_of(tuple))
    ppid = attr.ib(validator=instance_of(int))
    ptype = attr.ib(validator=instance_of(PointType))
    collisions = attr.ib(validator=instance_of(np.uint64))
    radius = attr.ib(validator=instance_of(float))
    tree_type = attr.ib(validator=instance_of(TreeType))


def connect_collisions_to_neural_points(collisions: np.ndarray, neuron):
    """
    For each point in the neural tree, find the closest collision
    value. This doesn't yet deal with two collision locations that
    are attributed to the same neural point.

    Returns:
    num_of_nodes: Number of raw points on that neuron.
    neural_points: Array of coordinates that make up the neuron.
    closest_cell_idx: Index to the closest point on the cell contour to the given collision.
    """
    num_of_nodes = 0
    for tree in neuron.tree:
        num_of_nodes += tree.total_rawpoints

    neuronal_points = np.zeros((num_of_nodes, 3), dtype=np.float64)
    idx = 0
    for tree in neuron.tree:
        for point in tree.rawpoint:
            neuronal_points[idx] = point.P
            idx += 1

    assert collisions.shape[1] == neuronal_points.shape[1]  # two 3D coordinate arrays
    dist = np.zeros(collisions.shape[0])
    splits = np.linspace(
        0, collisions.shape[0], num=1000, endpoint=False, dtype=np.int
    )[1:]
    split_colls = np.split(collisions, splits)
    neuronal_points_iterable = (neuronal_points for idx in range(len(splits)))
    zipped_args = zip(split_colls, neuronal_points_iterable)

    with mp.Pool() as pool:
        closest_cell_idx = pool.starmap(_dist_and_min, zipped_args)

    closest_cell_idx = np.concatenate(closest_cell_idx)
    return num_of_nodes, neuronal_points, closest_cell_idx


def _dist_and_min(colls, neuronal_points):
    return scipy.spatial.distance.cdist(colls, neuronal_points).argmin(axis=1)


def coerce_collisions_to_neural_coords(neuronal_points, closest_cell_idx: np.ndarray):
    """
    Counts the number of collisions per neuronal coordinate on the neuronal tree.
    If there are duplicate collisions it finds the neuronal coordinate which was closest to the
    collision point and discards the other point.
    Parameters:
    :param np.ndarray mindist: A 1D array with the length of the entire collisions array
    assi
    """
    neural_collisions = np.zeros(neuronal_points.shape[0], dtype=np.uint64)
    uniques, counts = np.unique(closest_cell_idx, return_counts=True)
    neural_collisions[uniques] = counts
    return neural_collisions


def make_collision_df(collisions, neuron, num_of_nodes) -> pd.DataFrame:
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
    assert num_of_nodes == collisions.shape[0]

    df = pd.DataFrame(
        {
            "source": np.zeros(num_of_nodes - neuron.total_trees, dtype=object),
            "target": np.zeros(num_of_nodes - neuron.total_trees, dtype=object),
            "distance": np.zeros(num_of_nodes - neuron.total_trees),
        }
    )
    print("Starting the tree parsing...")
    pair_number = 0
    for tree in neuron.tree:
        print(f"Parsing tree {tree.type}")
        parent_node = CollisionNode(
            loc=tuple(tree.rawpoint[0].P),
            ppid=-1,
            ptype=PointType.STANDARD,
            collisions=collisions[pair_number],
            radius=tree.rawpoint[0].r,
            tree_type=TreeType.from_str(tree.type),
        )
        new_node = CollisionNode(
            loc=tuple(tree.rawpoint[1].P),
            ppid=0,
            ptype=PointType.from_str(tree.rawpoint[1].ptype),
            collisions=collisions[1],
            radius=tree.rawpoint[1].r,
            tree_type=TreeType.from_str(tree.type),
        )
        dist = 0
        df.iloc[pair_number] = [parent_node, new_node, dist]
        pair_number += 1
        for point in tree.rawpoint[2:]:
            prev_node = new_node
            del new_node
            new_node = CollisionNode(
                loc=tuple(point.P),
                ppid=point.ppid,
                ptype=PointType.from_str(point.ptype),
                collisions=collisions[pair_number],
                radius=point.r,
                tree_type=TreeType.from_str(tree.type),
            )
            dist = mytools.Get_FiberDistance_Between_RawPoints(
                tree, prev_node.ppid, point.ppid
            )
            df.iloc[pair_number] = [prev_node, new_node, dist]
            pair_number += 1
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


def generate_graph(df: pd.DataFrame):
    return nx.convert_matrix.from_pandas_edgelist(
        df, source="source", target="target", edge_attr=True, create_using=nx.DiGraph
    )


@contextlib.contextmanager
def load_neuron(fname):
    """
    Uses py3DN's Load_Neuron function to load an XML representation
    of a NeuroLucida neuron into memory.
    Uses a context manager since it mingles with sys.path, and
    we wish to leave it unchanged at the end of the execution.
    """
    sys.path.append(str(pathlib.Path(__file__).resolve().parents[3] / "py3DN"))
    import NeuroLucidaXMLParser

    neuron = NeuroLucidaXMLParser.Load_Neuron(fname, 0.17, False)
    try:
        yield neuron
    finally:
        sys.path.pop(-1)


if __name__ == "__main__":
    neuron_fname = "/data/simulated_morph_data/neurons/AP120410_s1c1.xml"
    collisions_fname = "/data/simulated_morph_data/results/2019_2_10/normalized_agg_AP120410_s1c1_thresh_0.npz"
    collisions = np.load(collisions_fname)
    with load_neuron(neuron_fname) as neuron:
        num_of_nodes, neuronal_points, dist = connect_collisions_to_neural_points(
            collisions["neuron_coords"], neuron
        )
        neural_collisions = coerce_collisions_to_neural_coords(neuronal_points, dist)
        df = make_collision_df(neural_collisions, neuron, num_of_nodes)
        graph = generate_graph(df)

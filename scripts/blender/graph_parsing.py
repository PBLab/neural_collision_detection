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
import matplotlib.pyplot as plt
import attr
from attr.validators import instance_of

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
    radius = attr.ib(validator=instance_of(float))
    tree_type = attr.ib(validator=instance_of(TreeType))
    collisions = attr.ib(default=np.uint64(0), validator=instance_of(np.uint64))


@attr.s
class NeuronToGraph:
    """
    Ordered methods to convert an NeuroLucida XML representation of a neuron,
    possibly with collision data, to a networkx directed graph.
    """

    neuron_name = attr.ib(validator=instance_of(str))
    result_folder = attr.ib(validator=instance_of(str))
    thresh = attr.ib(validator=instance_of(int))
    with_collisions = attr.ib(default=True, validator=instance_of(bool))
    parent_folder = attr.ib(init=False)
    num_of_nodes = attr.ib(init=False)
    graph = attr.ib(init=False)

    def main(self):
        """ Main entrance to pipeline """
        self.parent_folder = pathlib.Path(__file__).parents[3].resolve()
        neuron_fname, collisions_fname, image_graph_fname, graph_fname = self._filename_setup(
            self.parent_folder, self.neuron_name, self.result_folder, self.thresh
        )
        with self._load_neuron(neuron_fname) as neuron:
            self.num_of_nodes = self._get_num_of_nodes(neuron)
            if self.with_collisions:
                collisions = np.load(str(collisions_fname))
            else:
                collisions = np.zeros(self.num_of_nodes)
            neuronal_points = self._extract_neuronal_coords(self.num_of_nodes, neuron)
            closest_cell = self._connect_collisions_to_neural_points(
                self.num_of_nodes, collisions["neuron_coords"], neuron, neuronal_points
            )
            neural_collisions = self._coerce_collisions_to_neural_coords(
                neuronal_points, closest_cell
            )
            collision_df = self._make_collision_df(
                neural_collisions, neuron, self.num_of_nodes
            )

        self.graph = self._generate_graph(collision_df)
        self._show_graph(self.graph, title=self.neuron_name, fname=image_graph_fname)
        self._serialize_graph(self.graph, graph_fname)

    def _get_num_of_nodes(self, neuron) -> int:
        """ Count number of nodes on an XML neuron """
        num_of_nodes = 0
        for tree in neuron.tree:
            num_of_nodes += tree.total_rawpoints
        return num_of_nodes

    def _filename_setup(
        self,
        parent_folder: pathlib.Path,
        neuron_name: str,
        result_foldername: str,
        thresh: int,
    ):
        """
        Finds all needed files for the scripts to run
        """
        parent_folder = parent_folder.resolve()
        neuron_fname = parent_folder / "neurons" / (neuron_name + ".xml")
        full_res_folder = parent_folder / "results" / result_foldername
        collisions_fname = (
            full_res_folder
            / f"normalized_agg_results_{neuron_name}_thresh_{thresh}.npz"
        )
        image_graph_fname = full_res_folder / f"image_graph_{neuron_name}"
        graph_fname = full_res_folder / f"graph_{neuron_name}.gexf"
        return neuron_fname, collisions_fname, image_graph_fname, graph_fname

    def _extract_neuronal_coords(self, num_of_nodes: int, neuron):
        """
        Parses the neuronal tree, populating an array with the coordinates
        of all the points in that tree (in Euclidean space).
        """
        neuronal_points = np.zeros((num_of_nodes, 3), dtype=np.float64)
        idx = 0
        for tree in neuron.tree:
            for point in tree.rawpoint:
                neuronal_points[idx] = point.P
                idx += 1
        return neuronal_points

    def _connect_collisions_to_neural_points(
        self,
        num_of_nodes: int,
        collisions: np.ndarray,
        neuron,
        neuronal_points: np.ndarray,
    ):
        """
        For each point in the neural tree, find the closest collision
        value. This doesn't yet deal with two collision locations that
        are attributed to the same neural point.

        Returns:
        num_of_nodes: Number of raw points on that neuron.
        neural_points: Array of coordinates that make up the neuron.
        closest_cell_idx: Index to the closest point on the cell contour to the given collision.
        """
        assert (
            collisions.shape[1] == neuronal_points.shape[1]
        )  # two 3D coordinate arrays
        splits = np.linspace(
            0, collisions.shape[0], num=1000, endpoint=False, dtype=np.int
        )[1:]
        split_colls = np.split(collisions, splits)
        neuronal_points_iterable = (neuronal_points for idx in range(len(splits)))
        zipped_args = zip(split_colls, neuronal_points_iterable)

        with mp.Pool() as pool:
            closest_cell_idx = pool.starmap(self._dist_and_min, zipped_args)

        closest_cell_idx = np.concatenate(closest_cell_idx)
        return closest_cell_idx

    def _dist_and_min(self, colls, neuronal_points):
        return scipy.spatial.distance.cdist(colls, neuronal_points).argmin(axis=1)

    def _coerce_collisions_to_neural_coords(
        self, neuronal_points, closest_cell_idx: np.ndarray
    ):
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

    def _make_collision_df(self, collisions, neuron, num_of_nodes) -> pd.DataFrame:
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

    def _generate_graph(self, df: pd.DataFrame):
        return nx.convert_matrix.from_pandas_edgelist(
            df,
            source="source",
            target="target",
            edge_attr=True,
            create_using=nx.DiGraph,
        )

    def _show_graph(self, g: nx.DiGraph, title: str = "Neuron", fname=None):
        fig, ax = plt.subplots()
        nx.draw(g, node_size=5, with_labels=False, alpha=0.5)
        ax.set_title(title)
        if fname:
            for suffix in [".eps", ".png", ".pdf"]:
                fig.savefig(str(fname) + suffix, transparent=True, dpi=300)

    def _serialize_graph(self, g: nx.DiGraph, fname: pathlib.Path):
        """ Write graph g to disk """
        nx.write_gexf(g, str(fname))

    @contextlib.contextmanager
    def _load_neuron(self, fname: pathlib.Path):
        """
        Uses py3DN's Load_Neuron function to load an XML representation
        of a NeuroLucida neuron into memory.
        Uses a context manager since it mingles with sys.path, and
        we wish to leave it unchanged at the end of the execution.
        """
        sys.path.append(str(self.parent_folder / "py3DN"))
        import NeuroLucidaXMLParser

        neuron = NeuroLucidaXMLParser.Load_Neuron(str(fname), 0.17, False)
        try:
            yield neuron
        finally:
            sys.path.pop(-1)


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


if __name__ == "__main__":
    neuron_name = "AP120410_s3c1"
    result_folder = "2019_2_10"
    thresh = 0
    with_collisions = True
    graphed_neuron = NeuronToGraph(
        neuron_name=neuron_name,
        result_folder=result_folder,
        thresh=thresh,
        with_collisions=with_collisions,
    )
    graphed_neuron.main()


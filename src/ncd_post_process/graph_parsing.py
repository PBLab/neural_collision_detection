import enum
import pathlib
import sys
import contextlib
import multiprocessing as mp
import functools
import re

import numpy as np
import networkx as nx
import attr
import pandas as pd
from attr.validators import instance_of, in_
import scipy.spatial.distance
import matplotlib.pyplot as plt
import numba as nb
from scipy.io import loadmat

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "py3DN"))
import mytools

# Define basic types of points and trees - can't use an
# Enum or class due to memory constraints
POINTTYPE = ["standard", "node", "endpoint"]
TREETYPE = [
    "Axon0",
    "Axon1",
    "Dendrite0",
    "Dendrite1",
    "Dendrite2",
    "Dendrite3",
    "Dendrite4",
    "Dendrite5",
]


@attr.s(frozen=True, slots=True)
class CollisionNode:
    """
    A single node on a neuronal tree.
    It's frozen since it has to be hashable in order to
    be allocated to a graph, and slots helps since we create thousands
    of it.

    :param int ord_number: Ordinal number of the point.
    :param np.ndarray loc: a 3-sized vector with coordinates.
    :param int ppid: parent point ID.
    :param str ptype: Type of point, one of POINTTYPE's values
    :param float radius: Radius of point
    :param str tree_type: Type of tree, one of TREETYPE's values
    :param np.float64 collision_chance: Probability of collision for the node
    :param np.float64 dist_to_body: topological distance to the cell body
    :param np.float64 alpha: Highest alpha value that contains this point
    """

    ord_number = attr.ib(validator=instance_of(int))
    loc = attr.ib(validator=instance_of(tuple))
    ppid = attr.ib(validator=instance_of(int))
    ptype = attr.ib(validator=in_(POINTTYPE))
    radius = attr.ib(validator=instance_of(float))
    tree_type = attr.ib(validator=in_(TREETYPE))
    collision_chance = attr.ib(default=np.float64(0), validator=instance_of(np.float64))
    dist_to_body = attr.ib(default=np.float64(0), validator=instance_of(np.float64))
    alpha = attr.ib(default=np.float64(0), validator=instance_of(np.float64))

    @classmethod
    def from_str(cls, string):
        """
        Create an instance from a string representation (repr)
        of the class.
        Usually used when deserializing data.
        """
        all_matches_regex = re.compile(
            r"ord_number=(\d+), loc=(\(.+?\)), ppid=(.+?), ptype='(\w+)', radius=(.+?), tree_type='(\w+)', collision_chance=(.+?), dist_to_body=(.+?), alpha=(.+?)\)"
        )
        matches = all_matches_regex.findall(string)[0]
        ord_number = int(matches[0])
        loc = eval(matches[1], {"__builtins__": tuple}, {})  # ¯\_(ツ)_/¯
        ppid = int(matches[2])
        ptype = matches[3]
        radius = float(matches[4])
        tree_type = matches[5]
        collision_chance = np.float64(matches[6])
        dist_to_body = np.float64(matches[7])
        alpha = np.float64(matches[8])

        return cls(
            ord_number,
            loc,
            ppid,
            ptype,
            radius,
            tree_type,
            collision_chance,
            dist_to_body,
            alpha,
        )


@attr.s
class NeuronToGraph:
    """
    Ordered methods to convert an NeuroLucida XML representation of a neuron,
    possibly with collision data, to a networkx directed graph. Use the "main"
    method to run the pipeline after initializing the object.

    Parameters:
    :param str neuron_name: Tag of current neuron
    :param str result_folder: Folder to save plotting and serialization results in.
    :paramm int thresh: Distance in um that signifies a valid collision from the aggregator functions
    :param bool with_collisions: Whether to look for collisions that were calculated for that specific neuron or not
    :paramm bool with_plot: Whether to plot the neuron or not
    :param bool with_serialize: Whether to write the graph to the disk
    :param bool inner_multiprocess: Whether to use multiprocessing in internal methods.
        Defaults to false since usually this whole module is called in a MP context.
    """

    neuron_name = attr.ib(validator=instance_of(str))
    result_folder = attr.ib(validator=instance_of(str))
    thresh = attr.ib(validator=instance_of(int))
    with_collisions = attr.ib(default=True, validator=instance_of(bool))
    with_plot = attr.ib(default=False, validator=instance_of(bool))
    with_serialize = attr.ib(default=True, validator=instance_of(bool))
    inner_multiprocess = attr.ib(default=False, validator=instance_of(bool))
    parent_folder = attr.ib(init=False)
    num_of_nodes = attr.ib(init=False)
    collisions = attr.ib(init=False)
    coll_prob = attr.ib(init=False)
    neuronal_points = attr.ib(init=False)
    closest_cell = attr.ib(init=False)
    graph = attr.ib(init=False)
    collisions_df = attr.ib(init=False)
    closest_coll = attr.ib(init=False)
    alpha = attr.ib(init=False)

    def run(self):
        """
        Main entrance to pipeline.
        If collisions exists it uses their real value and creates a graph
        with the actual collision value inside the node's attributes. Else,
        The nodes will contain 0 as their collision value.
        """
        self.parent_folder = pathlib.Path("/data/neural_collision_detection")
        (
            neuron_fname,
            collisions_fname,
            image_graph_fname,
            graph_fname,
        ) = self._filename_setup(
            self.parent_folder, self.neuron_name, self.result_folder, self.thresh
        )
        # TODO: Find out why AP120412_s3c2 has weird probabilities in its graph
        with load_neuron(self.parent_folder / "py3DN", neuron_fname) as neuron:
            self.num_of_nodes = self._get_num_of_nodes(neuron)
            self.neuronal_points = self._extract_neuronal_coords(
                self.num_of_nodes, neuron
            )
            if self.with_collisions:
                self.collisions = np.load(str(collisions_fname))["unique_coords"]
                self.coll_prob = np.load(str(collisions_fname))["coll_prob"]
                self.closest_coll = connect_collisions_to_neural_points(
                    self.collisions, self.neuronal_points, self.inner_multiprocess
                )
                self.alpha = loadmat(
                    collisions_fname.with_name(
                        f"{self.neuron_name}_balls_alpha_values.mat"
                    )
                )["first_alpha_per_point"].ravel()
                coll_prob = coerce_collisions_to_neural_coords(
                    len(self.neuronal_points), self.closest_coll, self.coll_prob,
                )

            else:
                coll_prob = np.zeros(self.num_of_nodes, dtype=np.float64)
            self.collision_df = self._make_collision_df(
                coll_prob, neuron, self.num_of_nodes, self.alpha
            )

        self.graph = self._generate_graph(self.collision_df)
        if self.with_plot:
            self._show_graph(
                self.graph, title=self.neuron_name, fname=image_graph_fname
            )
        if self.with_serialize:
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
        neuron_fname = parent_folder / "data" / "neurons" / (neuron_name + ".xml")
        full_res_folder = parent_folder / "results" / result_foldername
        collisions_fname = (
            full_res_folder
            / f"normalized_agg_results_{neuron_name}_thresh_{thresh}.npz"
        )
        image_graph_fname = full_res_folder / f"image_graph_{neuron_name}"
        graph_fname = full_res_folder / f"graph_{neuron_name}.gml"
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
        return pd.DataFrame(neuronal_points, columns=["x", "y", "z"])

    def _make_collision_df(
        self, collisions, neuron, num_of_nodes, alpha
    ) -> pd.DataFrame:
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
        :param np.ndarray alpha: Alpha value per neuronal point.
        """
        assert num_of_nodes == collisions.shape[0]

        df = pd.DataFrame(
            {
                "source": np.zeros(num_of_nodes - neuron.total_trees, dtype=object),
                "target": np.zeros(num_of_nodes - neuron.total_trees, dtype=object),
                "weight": np.zeros(num_of_nodes - neuron.total_trees),
            }
        )
        print("Starting the tree parsing...")
        pair_number = 0
        for tree_idx, tree in enumerate(neuron.tree):
            tree_type = f"{tree.type}{tree_idx}"
            print(f"Parsing tree {tree_type}")
            parent_node = CollisionNode(
                ord_number=0,
                loc=tuple(tree.rawpoint[0].P),
                ppid=-1,
                ptype="standard",
                collision_chance=collisions[pair_number],
                radius=tree.rawpoint[0].r,
                tree_type=tree_type,
                dist_to_body=np.float64(0),
                alpha=alpha[0],
            )
            new_node = CollisionNode(
                ord_number=1,
                loc=tuple(tree.rawpoint[1].P),
                ppid=0,
                ptype=tree.rawpoint[1].ptype,
                collision_chance=collisions[1],
                radius=tree.rawpoint[1].r,
                tree_type=tree_type,
                dist_to_body=np.float64(0),
                alpha=alpha[1],
            )
            weight = np.float64(0)
            df.iloc[pair_number] = [parent_node, new_node, weight]
            pair_number += 1
            for point in tree.rawpoint[2:]:
                prev_node = new_node
                del new_node
                try:
                    weight = mytools.Get_FiberDistance_Between_RawPoints(
                        tree, 0, point.ppid
                    )
                except IndexError:
                    weight = np.float64(0)
                new_node = CollisionNode(
                    ord_number=pair_number + 1,
                    loc=tuple(point.P),
                    ppid=point.ppid,
                    ptype=point.ptype,
                    collision_chance=collisions[pair_number],
                    radius=point.r,
                    tree_type=tree_type,
                    dist_to_body=weight,
                    alpha=alpha[pair_number],
                )

                df.iloc[pair_number] = [prev_node, new_node, weight]
                pair_number += 1
        return df

    def _generate_graph(self, df: pd.DataFrame):
        return nx.convert_matrix.from_pandas_edgelist(
            df, source="source", target="target", edge_attr=True, create_using=nx.Graph
        )

    def _show_graph(self, g: nx.Graph, title: str = "Neuron", fname=None):
        fig, ax = plt.subplots()
        nx.draw(g, node_size=5, with_labels=False, alpha=0.5)
        ax.set_title(title)
        if fname:
            fname = str(fname)
            if self.with_collisions:
                fname += "_with_collisions"
            else:
                fname += "_no_collisions"
            for suffix in [".eps", ".png", ".pdf"]:
                fig.savefig(str(fname) + suffix, transparent=True, dpi=300)

    def _serialize_graph(self, g: nx.Graph, fname: pathlib.Path):
        """ Write graph g to disk """
        fname: str = str(fname)
        if self.with_collisions:
            fname = fname.replace(".gml", "_with_collisions.gml")
        else:
            fname = fname.replace(".gml", "_no_collisions.gml")
        nx.write_gml(g, fname, repr)


@attr.s
class CsvNeuronToGraph:
    """Creates a networkx graph instance from neurons in an .obj format """

    neuron_fname = attr.ib(validator=instance_of(pathlib.Path))
    results_folder = attr.ib(validator=instance_of(pathlib.Path))
    thresh = attr.ib(instance_of(int))
    neuron_coords = attr.ib(init=False)
    parent_folder = attr.ib(init=False)
    collisions = attr.ib(init=False)
    neuronal_points = attr.ib(init=False)
    closest_cell = attr.ib(init=False)
    graph = attr.ib(init=False)
    collisions_df = attr.ib(init=False)
    coll_prob = attr.ib(init=False)
    alpha = attr.ib(init=False)

    def main(self):
        """Main Pipeline"""
        (
            neuron_name,
            collisions_fname,
            image_graph_fname,
            graph_fname,
        ) = self._filename_setup()
        self.neuron_coords = self._load_neuron()
        self.collisions = np.load(str(collisions_fname))["unique_coords"]
        self.coll_prob = np.load(str(collisions_fname))["coll_prob"]
        self.alpha = loadmat(alpha_fname)["first_alpa_per_collision"].ravel()
        self._connect_collisions_to_neural_coords(neuron_name)

    def _filename_setup(self):
        """Finds needed files for this class to run."""
        neuron_name = self.neuron_fname.stem
        collisions_fname = (
            self.results_folder
            / f"normalized_agg_results_{neuron_name}_thresh_{self.thresh}.npz"
        )
        image_graph_fname = self.results_folder / f"image_graph_{neuron_name}.png"
        graph_fname = self.results_folder / f"graph_{neuron_name}.gml"
        return neuron_name, collisions_fname, image_graph_fname, graph_fname

    def _load_neuron(self):
        return pd.read_csv(self.neuron_fname, header=None, names=["x", "y", "z", "r"])

    def _connect_collisions_to_neural_coords(self, neuron_name):
        """
        For each point in the neural tree, find the closest collision
        value. This doesn't yet deal with two collision locations that
        are attributed to the same neural point.

        Returns:
        neural_points: Array of coordinates that make up the neuron.
        closest_cell_idx: Index to the closest point on the cell contour to the given collision.
        """
        ntg = NeuronToGraph(neuron_name, str(self.results_folder), self.thresh)
        closest_coll = connect_collisions_to_neural_points(
            self.collisions, self.neuron_coords, multiprocessed=False
        )
        coll_prob = coerce_collisions_to_neural_coords(
            len(self.neuron_coords), self.coll_prob, closest_coll,
        )
        collisions_df = ntg._make_collision_df(coll_prob)


def connect_collisions_to_neural_points(
    collisions: np.ndarray, neuronal_points: pd.DataFrame, multiprocessed=False
):
    """
    For each point in the neural tree, find the closest collision
    value. This doesn't yet deal with two collision locations that
    are attributed to the same neural point.

    Returns
    -------
        closest_coll_idx: Index to the closest collision for that given neural point
    """
    neuronal_points = neuronal_points.loc[:, "x":"z"]
    assert collisions.shape[1] == neuronal_points.shape[1]  # two 3D coordinate arrays
    return dist_and_min(collisions, neuronal_points)


def dist_and_min(colls, neuronal_points):
    """Calculates the distance between each collision and neural point, and
    returns the minimal

    """
    dist = scipy.spatial.distance.cdist(colls, neuronal_points)
    return dist.argmin(axis=0)


@contextlib.contextmanager
def load_neuron(py3dn_folder: pathlib.Path, fname: pathlib.Path):
    """
    Uses py3DN's Load_Neuron function to load an XML representation
    of a NeuroLucida neuron into memory.
    Uses a context manager since it mingles with sys.path, and
    we wish to leave it unchanged at the end of the execution.
    """
    sys.path.append(str(py3dn_folder))
    import NeuroLucidaXMLParser

    neuron = NeuroLucidaXMLParser.Load_Neuron(str(fname), 0.17, False)
    try:
        yield neuron
    finally:
        sys.path.pop(-1)


@nb.njit
def coerce_collisions_to_neural_coords(
    num_neuronal_points: int, closest_coll_idx: np.ndarray, coll_prob: np.ndarray,
):
    """Finds the collision probability of each neuronal point.

    This jitted function iterates over the neuron and assigns the collision probability
    of the closest collision to an array with the length of the neuron.

    Note
    ----
    The implementation is currently straight forward due to a few bugs in the past. The
    function is currently being evaluated for correctness.

    Parametres
    ----------
    num_neuronal_points : int
        Number of points the neuron is made of
    closest_coll_idx : np.ndarray
        An array with the length of num_neural_points, with its values indexing the
        collision array for the closest collision to that neural point
    coll_prob : np.ndarray
        An array with the length of the number of collisions which contains the
        probability of each collision

    Returns
    -------
    result : np.ndarray
        An array with the length of num_neuronal_points containing the calculated
        probability of collision for each neural point
    """
    prob_per_point = np.zeros(num_neuronal_points)
    for idx, closest_coll in enumerate(closest_coll_idx):
        prob_per_point[idx] = coll_prob[closest_coll]
    return prob_per_point


def mp_main(neuron_name, results_folder, thresh, with_collisions, with_plot=False):
    """Run the pipeline in a parallel manner."""
    try:
        graphed_neuron = NeuronToGraph(
            neuron_name=neuron_name,
            result_folder=result_folder,
            thresh=thresh,
            with_collisions=with_collisions,
            with_plot=with_plot,
        )
        graphed_neuron.run()
        return graphed_neuron
    except FileNotFoundError:
        print(f"File {neuron_name} not found")
        return


if __name__ == "__main__":
    neuron_names = [
        "AP120410_s1c1",
        "AP120410_s3c1",
        "AP120412_s3c2",
        "AP120416_s3c1",
        "AP120419_s1c1",
        "AP120420_s1c1",
        "AP120420_s2c1",
        "AP120507_s3c1",
        "AP120510_s1c1",
        "AP120522_s3c1",
        "AP120524_s2c1",
        "AP120614_s1c2",
        "AP130312_s1c1",
        "AP131105_s1c1",
    ]
    result_folder = "2020_02_14"
    thresh = 0
    with_collisions = True
    with_plot = False

    args = [
        (neuron_name, result_folder, thresh, with_collisions, with_plot)
        for neuron_name in neuron_names
    ]
    # multicore execution
    with mp.Pool() as pool:
        objs = pool.starmap(mp_main, args)

    # obj = [mp_main(*arg) for arg in args]  # single core execution

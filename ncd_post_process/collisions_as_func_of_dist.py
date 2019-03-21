import pathlib
import multiprocessing
import itertools
from typing import List, Tuple
from collections import namedtuple
import copy

import numpy as np
import attr
from attr.validators import instance_of
import scipy.interpolate
import scipy.spatial
import networkx as nx

from graph_parsing import CollisionNode, NeuronToGraph

NodesAndCoords = namedtuple("NodesAndCoords", ["as_nodes", "as_coords"])


@attr.s
class CollisionsAndDistance:
    """
    Correlates and plots the number of collisions
    between the neuron and the surrounding vasculature
    as a function of their distance - either topological
    or Euclidean
    """

    nrn_to_graph = attr.ib(validator=instance_of(NeuronToGraph))
    nodes_array = attr.ib(init=False)
    coll_topo_dist = attr.ib(init=False)
    coll_euclid_dist = attr.ib(init=False)

    def run(self):
        self.nodes_array = self._create_nodes_array()
        print("Finding coords...")
        nodes_coords = self._find_coords_for_closest_nodes_per_coll(
            self.nrn_to_graph.closest_cell
        )
        print("Calc topo distance...")
        dists = self._calc_topo_dist_per_coll(nodes_coords)
        self.coll_topo_dist = self._match_dist_to_node(
            dists, nodes_coords
        )
        self.coll_euclid_dist = self._calc_collision_euc_distance_to_origin()

    def _create_nodes_array(self):
        """ Transform the graph into an ordered 1D vector """
        nodes_array = np.zeros(
            (self.nrn_to_graph.neuronal_points.shape[0]), dtype="object"
        )
        for node in self.nrn_to_graph.graph.nodes():
            nodes_array[node.ord_number] = copy.deepcopy(node)
        return nodes_array

    def _find_coords_for_closest_nodes_per_coll(
        self, closest_node_per_coll
    ) -> List[NodesAndCoords]:
        """
        Return list populated with small numpy arrays which contain the coordinates
        of the points on top of the neuron closest to a given collision and the nodes
        that "own" these coordinates
        """
        all_nodes_with_colls = self.nodes_array[closest_node_per_coll]
        zipped_args = ((node, self.nrn_to_graph.graph) for node in all_nodes_with_colls)
        with multiprocessing.Pool() as pool:
            nodes_coords = pool.starmap(self._find_four_closest, zipped_args)
        return nodes_coords

    def _find_four_closest(
        self, node: CollisionNode, graph: nx.Graph
    ) -> NodesAndCoords:
        """
        For a given node index in the graph, find the four closest nodes topologically
        to that node. Generate a coordinate array from these four nodes + the
        original one.
        """
        neighboring_nodes: List[CollisionNode] = []
        neighboring_nodes = self._get_neighbors(neighboring_nodes, node, graph)
        neighboring_nodes.insert(2, node)
        coord_array = np.zeros((5, 3))
        for idx, node in enumerate(neighboring_nodes):
            coord_array[idx, :] = np.array(node.loc)

        return NodesAndCoords(neighboring_nodes, coord_array)

    def _get_neighbors(self, found_neighbors, node, graph) -> List[CollisionNode]:
        """
        Traverses the given graph both ways to find the four closets neighbors
        to the origin node.
        """
        while len(found_neighbors) < 4:
            if node:
                prev, next_ = graph[node]  # retrieves neighbors
                if prev:
                    found_neighbors.append(prev)
                if next_:
                    found_neighbors.append(next_)
                self._get_neighbors(found_neighbors, prev, graph)
                self._get_neighbors(found_neighbors, next_, graph)
        return found_neighbors

    def _calc_topo_dist_per_coll(
        self, nodes_coords
    ) -> List[Tuple[np.uint32, np.float64]]:
        """
        Calculates the exact topological distance of each
        collision from the cell's soma.
        Returns a list of tuples, each one containing the coordinate of the
        point as an array and the distance to that point
        """
        args = (
            (coll, node_coord.as_coords)
            for coll, node_coord in zip(self.nrn_to_graph.collisions, nodes_coords)
        )
        with multiprocessing.Pool() as pool:
            point_idx_and_dist = pool.starmap(FindClosestPoint(), args)
        return point_idx_and_dist

    def _match_dist_to_node(
        self,
        dists: List[Tuple[np.uint32, np.float64]],
        nodes_coords: List[NodesAndCoords],
    ) -> np.ndarray:
        """
        Iterates over the computed distances and all the nodes and
        matches a distance with its corresponding node.
        """
        assert len(dists) == len(nodes_coords)
        topo_dist_of_each_coll = np.zeros(len(dists))
        for idx, (dist, node_coord) in enumerate(nodes_coords):
            cur_node = node_coord.as_nodes[dist[0]]
            topo_dist_of_each_coll[idx] = dist[1] + cur_node.dist_to_body

        return topo_dist_of_each_coll

@attr.s
class FindClosestPoint:
    """
    A specialized class designed to interpolate a small portion
    of a neuron in order to find the closest point on that neuron
    to a collision. In other words, it looks for the point on a
    neuron closest to a collision, albeit that point has to be
    first interpolated.

    Inputs:
    :param np.ndarray coll: Collision point (3D)
    :param np.ndarray points: Three relevant points on the neuron, 3x3 array.

    Returns (from run):
    :param Tuple[np.ndarray, float]: Coordinate of closest point and the distance to that point
    """

    coll = attr.ib(init=False)
    points = attr.ib(init=False)

    def __call__(self, coll, points):
        self.coll = coll
        self.points = points
        return self.run()

    def run(self) -> Tuple[np.uint32, np.float64]:
        """ Run pipeline """
        interped_points = self._interp_3d()

        closest_interped_point_to_coll = self._find_closest_interped_point(
            interped_points
        )
        distance_to_point_on_neuron, point_idx = self._find_next_closest_point(
            interped_points[closest_interped_point_to_coll]
        )
        return point_idx, distance_to_point_on_neuron

    def _interp_3d(self, num_points=100):
        """
        Generate num_points (default is 100) interpolated points between the 5 given points
        of the neuron using spline interpolation. These points will be used to
        find the closest one to another point.
        Returns an (num_points x 3) array of coordinates.
        """
        tck, u = scipy.interpolate.splprep(
            (self.points[:, 0], self.points[:, 1], self.points[:, 2]), s=2
        )
        u_fine = np.linspace(0, 1, num_points)
        x_fine, y_fine, z_fine = scipy.interpolate.splev(u_fine, tck)
        return np.array([x_fine, y_fine, z_fine])

    def _find_closest_interped_point(self, interped_points):
        """ Finds the closest point from the interpolated
        points to the collision """
        dist = scipy.spatial.distance.cdist(np.atleast_2d(self.coll), interped_points.T)
        return dist.argmin(axis=1)

    def _find_next_closest_point(self, coord) -> Tuple[np.float64, np.uint32]:
        """
        Connects the interpolated closest point to the closest point
        on the neuronal graph that exists. This helps us calculate the
        distance from the collision point to the soma. """
        dist = scipy.spatial.distance.cdist(np.atleast_2d(coord), self.points)
        return dist.min(axis=1), dist.argmin(axis=1)

    def _calc_collision_euc_distance_to_origin(self):
        """
        Creates a 1D vector with the distance of each collision
        from the cell center, i.e. the origin
        """
        origin = np.array([0., 0., 0.,])
        dists = scipy.spatial.distance.cdist(origin, self.nrn_to_graph.collisions)
        return dists



if __name__ == "__main__":
    neuron_name = "AP120410_s1c1"
    result_folder = "2019_2_10"
    thresh = 0
    with_collisions = True
    with_plot = False
    with_serialize = False
    inner_multiprocess = True
    ntg = NeuronToGraph(
        neuron_name,
        result_folder,
        thresh,
        with_collisions,
        with_plot,
        with_serialize,
        inner_multiprocess,
    )
    ntg.run()
    coll_dist = CollisionsAndDistance(ntg)
    coll_dist.run()

import pathlib

import numpy as np
import attr
from attr.validators import instance_of
import scipy.interpolate
import scipy.distance

from graph_parsing import (
    NeuronToGraph,
    connect_collisions_to_neural_points,
    dist_and_min,
)


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
        closest_cell_per_coll = connect_collisions_to_neural_points(
            self.nrn_to_graph.collisions, self.nrn_to_graph.neuronal_points
        )
        self._connect_coll_with_neuron_coord(self.nrn_to_graph, closest_cell_per_coll)

    def _create_nodes_array(self):
        """ Transform the graph into an ordered 1D vector """
        nodes_array = np.zeros(
            (self.nrn_to_graph.neuronal_points.shape[0]), dtype="object"
        )
        for node in self.nrn_to_graph.graph:
            nodes_array[node.ord_number] = node.copy()

    def _connect_coll_with_neuron_coord(self, nrn_graph, closest_cell):


    def calc_topo_dist(self):
        """
        Calculates the exact topological distance of each
        collision from the cell's soma.
        """
        assert self.nrn_to_graph.min_dist.shape == self.nrn_to_graph.closest_cell.shape


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
    :param np.ndarray: Coordinate of closest point and the distance to that point
    """

    coll = attr.ib(validator=instance_of(np.ndarray))
    points = attr.ib(validator=instance_of(np.ndarray))

    def run(self):
        """ Run pipeline """
        interped_points = self._interp_3d()
        closest_interped_point_to_coll = self._find_closest_interped_point(
            interped_points
        )
        distance_to_point_on_neuron, point_idx = self._find_next_closest_point(
            interped_points[closest_interped_point_to_coll]
        )
        return self.points[point_idx], distance_to_point_on_neuron

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

    def _find_next_closest_point(self, coord):
        """
        Connects the interpolated closest point to the closest point
        on the neuronal graph that exists. This helps us calculate the
        distance from the collision point to the soma. """
        dist = scipy.spatial.distance.cdist(np.atleast_2d(coord), self.points)
        return dist.min(axis=1), dist.argmin(axis=1)


if __name__ == "__main__":
    neuron_name = "AP120410_s1c1"
    result_folder = "2019_2_10"
    thresh = 0
    with_collisions = True
    with_plot = False
    with_serialize = False

    coll = np.array([100, -23.5, 45])
    points = np.array(
        [
            [89, -41.0, 30],
            [91, -36.1, 32],
            [94, -22.0, 41],
            [97, -17.6, 48.9],
            [101, -11.3, 49.9],
        ]
    )
    closest = FindClosestPoint(coll, points)
    retpoints = closest.run()

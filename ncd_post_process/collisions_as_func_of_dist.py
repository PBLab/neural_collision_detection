import pathlib

import numpy as np
import attr
from attr.validators import instance_of

from graph_parsing import NeuronToGraph


class CollisionsAndDistance:
    """
    Correlates and plots the number of collisions
    between the neuron and the surrounding vasculature
    as a function of their distance - either topological
    or Euclidean
    """
    nrn_to_graph = attr.ib(validator=instance_of(NeuronToGraph))
    coll_topo_dist = attr.ib(init=False)
    coll_euclid_dist = attr.ib(init=False)

    def run(self):
        self._connect_coll_with_neuron_coord(self.nrn_to_graph)

    def _connect_coll_with_neuron_coord(self, nrn_graph):
        

    def calc_topo_dist(self):
        """
        Calculates the exact topological distance of each
        collision from the cell's soma.
        """
        assert self.nrn_to_graph.min_dist.shape == self.nrn_to_graph.closest_cell.shape

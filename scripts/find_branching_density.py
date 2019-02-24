"""
Using a serialized neuron, finds the number of branching points
every point along the neuronal path has by wrapping it in spheres
and counting the number of branches inside it
"""
import pathlib

import numpy as np
import attr
from attr.validators import instance_of


@attr.s
class BranchDensity:
    pass
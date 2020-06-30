"""This file helps with finding interesting blocks that surround
some areas of the neuron, and will focus on them alone.
Should be run under blender.
"""
import sys

sys.path.append(
    "/data/neural_collision_detection/src"
)

import numpy as np

from ncd_post_process.blender import draw_bounding_boxes


coor = ((9.270000457763672, 37.900001525878906), (-101.86000061035156, -69.41999816894531), (-46.810001373291016, -21.969999313354492))

draw_bounding_boxes.draw_boxes(coor)


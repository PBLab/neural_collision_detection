import pathlib

import pandas as pd
import numpy as np
from scipy.io import loadmat
import seaborn as sns
import napari
from vispy.color import Colormap

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import CollisionsDistNaive
from overlay_collisions_napari import show_collisions_with_napari

graph_fname = pathlib.Path('/data/neural_collision_detection/results/2020_02_14/graph_AP130312_s1c1_with_collisions.gml')
g = CollisionsDistNaive.from_graph(graph_fname, 'AP130312_s1c1')
g.run()
points = g.all_colls.set_index('type')

properties = {'alpha': points["alpha"]}
# face_color_cycle = Colormap(['r', 'g', 'b'])[np.linspace(0., 1., 100.)]

# with napari.gui_qt():
#     viewer = napari.Viewer(ndisplay=3)
#     show_collisions_with_napari(points, viewer, 'AP130312_s1c1')
#     viewer.add_points(points.loc[:, "x":"z"], properties=properties, size=2, edge_width=0, face_color_cycle=face_color_cycle)

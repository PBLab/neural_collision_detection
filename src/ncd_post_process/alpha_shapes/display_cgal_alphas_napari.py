import pathlib

import napari
import numpy as np
import pandas as pd


foldername_alpha = pathlib.Path("/data/neural_collision_detection/results/for_article/fig2")
foldername_neurons = pathlib.Path("/data/neural_collision_detection/data/neurons")
ext_alpha = "_alpha_distrib.csv"
ext_neurons = "_balls.csv"
neuron_names = [
    "AP120507_s3c1",
    "AP131105_s1c1",
    "AP120410_s1c1",
    "AP120410_s3c1",
    "AP120412_s3c2",
    "AP120416_s3c1",
    "AP120419_s1c1",
    "AP120420_s1c1",
    "AP120420_s2c1",
    "AP120510_s1c1",
    "AP120524_s2c1",
    "AP120614_s1c2",
    "AP130312_s1c1",
]

full_neuron_names_alpha = [foldername_alpha / (neuron + ext_alpha) for neuron in neuron_names]
full_neuron_names_neurons = [foldername_neurons / (neuron + ext_neurons) for neuron in neuron_names]

for alpha, neuron in zip(full_neuron_names_alpha[:1], full_neuron_names_neurons[:1]):
    alphas = pd.read_csv(alpha)
    points = pd.read_csv(neuron, header=None, names=["x", "y", "z", "r"])
    alpha_values = pd.Series(alphas.columns)
    with napari.gui_qt():
        viewer = napari.Viewer(ndisplay=3)
        viewer.add_points(points.loc[:, "x":"z"], edge_width=0, name=f"{neuron_names[0]}_all", face_color="green")
        outside_points = points.loc[alphas.iloc[:, -1] == np.uint8(2), :]
        viewer.add_points(outside_points.loc[:, "x":"z"], edge_width=0, name=f"{neuron_names[0]}_outside", face_color="orange")

import pathlib

import napari
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.spatial.transform import Rotation

from ncd_post_process.render_with_napari import create_napari_surface
from ncd_post_process.alpha_shapes import distance_alpha


def norm(data1: np.ndarray, data2: np.ndarray, range_=(0, 15)):
    data1 = np.nan_to_num(data1)
    data2 = np.nan_to_num(data2)
    min_ = min(data1.min(), data2.min())
    max_ = max(data1.max(), data2.max())
    for datum in [data1, data2]:
        datum -= min_
        datum /= max_ / range_[1]
        datum += range_[0]
    return data1, data2
    # return data1 / 40, data2 / 40


foldername_alpha = pathlib.Path("/data/neural_collision_detection/results/with_alpha/")
foldername_neurons = pathlib.Path("/data/neural_collision_detection/data/neurons")
ext_alpha = "_alpha_distrib.h5"
ext_neurons = "_balls_yz_flipped.csv"
ext_pairs = "_closest_pairs.h5"
ext_surf = "_yz_flipped.obj"
neuron_names = [
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

full_neuron_names_alpha = [
    foldername_alpha / (neuron + ext_alpha) for neuron in neuron_names
]
full_neuron_names_neurons = [
    foldername_neurons / (neuron + ext_neurons) for neuron in neuron_names
]
full_neuron_names_pairs = [
    foldername_alpha / (neuron + ext_pairs) for neuron in neuron_names
]
full_neuron_names_surf = [
    foldername_neurons / (neuron + ext_surf) for neuron in neuron_names
]

# r = Rotation.from_euler('xzy', [[-90, -90, -90]], degrees=True)
with napari.gui_qt():
    viewer = napari.Viewer(ndisplay=3)

    for pair, neuron, surf, orig_name in zip(
        full_neuron_names_pairs[2:4],
        full_neuron_names_neurons[2:4],
        full_neuron_names_surf[2:4],
        neuron_names[2:4],
    ):
        pairs = pd.read_hdf(pair, "data_single_pair")
        points = pd.read_csv(neuron, header=None, names=["y", "x", "z", "r"])
        alphas = distance_alpha.main_alpha_pipe(orig_name, foldername_alpha)
        pairs = pairs.loc[pairs.loc[:, "alpha_delta"] > 100, :]
        normed_ax_size, normed_dend_size = norm(
            pairs.loc[:, "ax_alpha"].to_numpy().copy(),
            pairs.loc[:, "dend_alpha"].to_numpy().copy(),
            (1, 5),
        )
        normed_ax_size[normed_ax_size > 10] = 0
        normed_dend_size[normed_dend_size > 10] = 0
        surface = create_napari_surface(surf)
        ax_points = pairs.loc[:, "ax_x":"ax_z"]
        dend_points = pairs.loc[:, "dend_x":"dend_z"]
        viewer.add_points(
            points.loc[:, "y":"z"],
            edge_width=0,
            name=f"{orig_name}_all",
            face_color="magenta",
        )
        viewer.add_points(
            ax_points,
            edge_width=0,
            name=f"{orig_name}_ax",
            face_color="green",
            size=normed_ax_size,
            opacity=0.4,
        )
        viewer.add_points(
            dend_points,
            edge_width=0,
            name=f"{orig_name}_dend",
            face_color="orange",
            size=normed_dend_size,
            opacity=0.4,
        )
        viewer.add_surface(
            surface, colormap="magenta", opacity=1,
        )
        viewer.add_points(
            points.iloc[:, :3],
            edge_width=0,
            name=f"{orig_name}_alphas",
            face_color="blue",
            size=np.log(alphas + 1),
            opacity=0.4,
        )

import pathlib

import napari
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.render_with_napari import create_napari_surface
from ncd_post_process.alpha_shapes import distance_alpha

MAX_ALLOWED_ALPHA = 3163


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
    # "AP120410_s1c1",
    # "AP120410_s3c1",
    "AP120412_s3c2",
    # "AP120416_s3c1",
    # "AP120419_s1c1",
    # "AP120420_s1c1",
    # "AP120420_s2c1",
    # "AP120510_s1c1",
    # "AP120524_s2c1",
    # "AP120614_s1c2",
    "AP130312_s1c1",
]
metadata = (('green', 'ax'), ('orange', 'dend'))

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


def show_all_equal_size(v: napari.Viewer, data: pd.DataFrame, name: str):
    """Shows all points of a neuron in napari.

    Parameters
    ----------
    v : napari.Viewer
    data : pd.DataFrame
        data
    name : str
        Neuron's name
    """
    v.add_points(
        data.loc[:, "x":"z"],
        edge_width=0,
        name=f"{name}_all",
        face_color="magenta",
    )


def show_ax_dend(v: napari.Viewer, ax: pd.DataFrame, dend: pd.DataFrame, name: str):
    for (data, meta) in zip([ax, dend], metadata):
        v.add_points(
            data.loc[::10, "x":"z"],
            edge_width=0,
            name=f"{name}_{meta[1]}",
            face_color=f"{meta[0]}",
            size=data.loc[::10, 'alpha'],
            opacity=0.2,
        )


def separate_ax_dend(points: pd.DataFrame):
    ax = points.loc['Axon0']
    dend = points.loc[~points.index.isin(['Axon0'])]
    return ax, dend


def load_complete_neuronal_data(neuron_name: str, graph_folder: pathlib.Path):
    collisions_fname = graph_folder / f"graph_{neuron_name}_with_collisions.gml"
    try:
        points, g = distance_alpha.generate_df_from_neuron(collisions_fname, neuron_name)
    except FileNotFoundError:
        return
    return points, g


def show_pairs(viewer: napari.Viewer, data: pd.DataFrame):
    """Highlights interesting pairs from the axonal and dendritic trees."""
    viewer.add_points(
            data.loc[:, 'ax_x':'ax_z'],
            edge_width=0,
            name='ax',
            face_color='green',
            size=data.loc[:, 'ax_alpha'],
    )
    viewer.add_points(
            data.loc[:, 'dend_x':'dend_z'],
            edge_width=0,
            name='dend',
            face_color='orange',
            size=data.loc[:, 'dend_alpha'],
    )


def main():
    with napari.gui_qt():
        viewer = napari.Viewer(ndisplay=3)
        all_alphas = []
        for pair, neuron, surf, orig_name in zip(
            full_neuron_names_pairs,
            full_neuron_names_neurons,
            full_neuron_names_surf,
            neuron_names,
        ):
            pairs = pd.read_hdf(pair, "data_single_pair")
            pairs = pairs.loc[pairs.loc[:, "alpha_delta"] > 100, :]
            # alphas = distance_alpha.main_alpha_pipe(orig_name, foldername_alpha)
            points, graph = load_complete_neuronal_data(orig_name, pathlib.Path('results/2020_09_05'))
            points.loc[:, 'alpha'] = ((points.alpha / MAX_ALLOWED_ALPHA) * 2).clip(upper=20)
            pairs.loc[:, 'ax_alpha'] = ((pairs.ax_alpha / MAX_ALLOWED_ALPHA) * 2).clip(upper=20)
            pairs.loc[:, 'dend_alpha'] = ((pairs.dend_alpha / MAX_ALLOWED_ALPHA) * 2).clip(upper=20)
            ax, dend = separate_ax_dend(points)
            # try:
            #     normed_ax_size, normed_dend_size = norm(
            #         pairs.loc[:, "ax_alpha"].to_numpy().copy(),
            #         pairs.loc[:, "dend_alpha"].to_numpy().copy(),
            #         (1, 5),
            #     )
            # except ValueError:
            #     continue
            # normed_ax_size[normed_ax_size > 10] = 0
            # normed_dend_size[normed_dend_size > 10] = 0
            # surface = create_napari_surface(surf)
            # viewer.add_surface(
            #     surface, colormap="magenta", opacity=1,
            # )
            # show_all_equal_size(viewer, points, orig_name)
            show_ax_dend(viewer, ax, dend, orig_name)
            show_pairs(viewer, pairs)
            # all_alphas.append(alphas)
        plt.show(block=False)
    return points, orig_name


if __name__ == '__main__':
    points, name = main()

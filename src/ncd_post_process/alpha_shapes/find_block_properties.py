"""This module deals with dividing each neuron into sub-blocks in 3D space.
Once the neuron is divided we can calculate properties of that block.
Properties may include the distribution of alpha shapes, dist. of collisions,
axon-dendrite relations in the block and more."""

import pathlib
import multiprocessing

import numpy as np
import pandas as pd
import scipy.stats
import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    CollisionsDistNaive,
)


def find_points_bounding_box(points: pd.DataFrame) -> tuple:
    """Finds the 3D coordinates of the bounding box of the given array.

    Parameters
    ----------
    points : pd.DataFrame
        Points to parse

    Returns
    -------
    3-tuple of 2-tuples
        ((min(x), max(x)), (min(y), ...))
    """
    x_max, y_max, z_max = points.max(axis=0)
    x_min, y_min, z_min = points.min(axis=0)
    return ((x_min, x_max), (y_min, y_max), (z_min, z_max))


def load_neuronal_points(graph_fname: pathlib.Path, neuron_name: str) -> pd.DataFrame:
    """Loads the given gml filename and returns the dataframe
    that comprises the neuron.
    """
    g = CollisionsDistNaive.from_graph(graph_fname, neuron_name)
    g.run()
    points = g.all_colls
    return points


def divide_neuron_into_blocks(points: pd.DataFrame, blocks=(10, 10, 5)) -> np.ndarray:
    """Loads the given neuron into memory and returns a 1D array with the block number
    for each point.

    The neuron is expected to be loaded from a CSV file. The returned array's length
    is identical to the length of the neuron, and each points receives a block number
    that it was allocated into.

    Parameters
    ----------
    neuron : pathlib.Path
        3D neuron coordinates
    blocks : 3-tuple
        Number of blocks in each direction

    Returns
    -------
    np.ndarray
        1D array of block number per neuron coordinate. The number of unique values
        should equal prod(blocks)
    """
    bounding_box = find_points_bounding_box(points)
    linspace_per_ax = []
    for minmax, block in zip(bounding_box, blocks):
        bins = np.linspace(
            minmax[0], minmax[1], block + 1, endpoint=True, dtype=np.int32
        )
        linspace_per_ax.append(bins)
        print(f"The size of this block is {bins[1] - bins[0]} microns.")
    ret = scipy.stats.binned_statistic_dd(
        points.to_numpy(), np.arange(len(points)), "count",
    )
    return ret[2]


def divide_and_plot(all_data: pd.DataFrame):
    """Divides the given data frame into axonal and dendritic blocks,
    and plots them together on the same JointPlot.

    The functions tries to deal with situations where there are only axonal points
    and\or dendritic points.

    Parameters
    ----------
    all_data : pd.DataFrame
        A DF consisting of both axonal and dendritic data with a "type"
        column that separates them.
    """
    all_data.loc[:, "is_ax"] = all_data["type"].str.contains("Axon")
    axonal = all_data.query("is_ax == True")
    dendritic = all_data.query("is_ax == False")
    both = 0
    if not axonal.empty:
        g, bins = plot_distribution(axonal, color="C2")
        both += 1
    else:
        g = sns.JointGrid(x="coll", y="alpha", data=dendritic)
        bins = None
    if not dendritic.empty:
        g, _ = plot_distribution(dendritic, color="C1", g=g, bins=bins)
        both += 1
    if both == 2:
        bb = find_points_bounding_box(all_data.loc[:, "x":"z"])
        g.fig.suptitle("Alpha Value vs. Collision Chance for Axons (Green) and Dendrites")
        g.fig.savefig(f'/data/neural_collision_detection/results/for_article/fig2/coll_vs_alpha_{bb}.png', dpi=300, transparent=True)


def plot_distribution(data: pd.DataFrame, color, g=None, bins=None):
    """Plots a jointplot of the data.

    This plot is of a single block, showing the relation between
    the collision chance and the alpha value.

    Parameters
    ----------
    data : pd.DataFrame
        Table with collision and alpha information
    color : str
        Color of the elements
    g : sns.JointGrid, optional
        The JointGrid on which we'll draw. Creates it if it doesn't exist
    bins : dict, optional
        A dictionary with 'x' and 'y' keys containing the bin edges
    """
    if not g:
        g = sns.JointGrid(x="coll", y="alpha", data=data)
    if not bins:
        bins = dict(x=None, y=None)
    g.ax_joint.scatter(data["coll"], data["alpha"], c=color, s=7, alpha=0.6)
    _, binx, _ = g.ax_marg_x.hist(data["coll"], alpha=0.6, color=color, bins=bins["x"])
    _, biny, _ = g.ax_marg_y.hist(
        data["alpha"], alpha=0.6, color=color, orientation="horizontal", bins=bins["y"]
    )
    return g, {"x": binx, "y": biny}


if __name__ == "__main__":
    path = pathlib.Path(
        "results/2020_02_14/graph_AP120410_s1c1_with_collisions.gml"
    ).resolve()
    points = load_neuronal_points(path, "AP120410")
    indices = divide_neuron_into_blocks(points.loc[:, "x":"z"], (10, 19, 6))
    uniques = np.unique(indices)
    blocks = (points.iloc[indices == unique] for unique in uniques)
    with multiprocessing.Pool() as mp:
        mp.map(divide_and_plot, blocks)
    # for block in blocks:
    #     divide_and_plot(block)
    #     plt.show()

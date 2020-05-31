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
    print(f"The size of")
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


def plot_distribution(data: pd.DataFrame):
    """Plots a jointplot of the data, dividing
    axons and dendrites.

    This plot is of a single block, showing the relation between
    the collision chance and the alpha value.

    Parameters
    ----------
    data : pd.DataFrame
        Table with collision and alpha information
    """
    sns.jointplot(data=data, x="collisions", y="alpha")


if __name__ == "__main__":
    path = pathlib.Path(
        "results/2020_02_14/graph_AP120410_s1c1_with_collisions.gml"
    ).resolve()
    points = load_neuronal_points(path, "AP120410")
    indices = divide_neuron_into_blocks(points.loc[:, "x":"z"], (10, 10, 5))
    uniques = np.unique(indices)
    blocks = (points.iloc[unique] for unique in uniques)
    with multiprocessing.Pool() as mp:
        mp.map(plot_distribution, blocks)

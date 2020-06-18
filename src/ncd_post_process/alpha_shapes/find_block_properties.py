"""This module deals with dividing each neuron into sub-block in 3D space.
Once the neuron is divided we can calculate properties of that block.
Properties may include the distribution of alpha shapes, dist. of collisions,
axon-dendrite relations in the block and more."""

import pathlib
import multiprocessing
from typing import Tuple, List
from collections import defaultdict
import pickle

import numpy as np
import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt
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
    return ((x_min, x_max), (y_min, y_max), (z_min, z_max))


def load_neuronal_points(graph_fname: pathlib.Path, neuron_name: str) -> pd.DataFrame:
    """Loads the given gml filename and returns the dataframe
    that comprises the neuron.
    """
    g = CollisionsDistNaive.from_graph(graph_fname, neuron_name)
    g.run()
    points = g.all_colls
    return points


def divide_neuron_into_blocks(points: pd.DataFrame, blocks=(10, 10, 5)) -> Tuple[np.ndarray, List[np.ndarray]]:
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
    List of np.ndarray
        A list populated with an array of bin edges for each axis
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
        points.to_numpy(), np.arange(len(points)), "count", bins=linspace_per_ax
    )
    return ret[2], linspace_per_ax


def divide_and_plot(all_data: pd.DataFrame, data_folder: pathlib.Path, neuron_name: str):
    """Divides the given data frame into axonal and dendritic blocks
    and plots them together on the same JointPlot.

    The functions tries to deal with situations where there are only axonal points
    and\\or dendritic points.

    Parameters
    ----------
    all_data : pd.DataFrame
        A DF consisting of both axonal and dendritic data with a "type"
        column that separates them.
    """
    all_data.loc[:, "is_ax"] = all_data.loc[:, "type"].str.contains("Axon")
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
        _serialize_data(data_folder, bb, neuron_name)
        _serialize_fig(data_folder, bb, neuron_name, g.fig)


def _serialize_data(data_folder: pathlib.Path, bb: tuple, neuron_name: str):
    """Writes the given bounding box data to disk.
    
    The data is one of the bounding boxes of the current neuron, and it should
    be pickled alongside the rest of the bounding boxes of that neuron. This
    function will create a new pickle file if it doesn't exist, or update
    the current data if it's not there.

    Parameters
    ----------
    data_folder : pathlib.Path
        Folder to store the pickle file
    bb : 3-tuple of 2-tuple
        For each axis, start and end of bounding box
    neuron_name : str
    """
    pickle_fname = data_folder / "bb_coord_alpha_coll.pickle"
    try:
        with open(pickle_fname, 'rb') as f:
            data = pickle.load(f)
    except FileNotFoundError:
        data = defaultdict(list, {})
    if data not in data[neuron_name]:
        data[neuron_name].append(bb)
    with open(pickle_fname, 'w+b') as f:
        pickle.dump(data, f)
 

def _serialize_fig(data_folder: pathlib.Path, bb: tuple, neuron_name: str, fig: plt.Figure): 
    """Serialize the figure for the given neuron name.

    The function appends the bounding box (bb) of the data to the filename of the
    figure. 

    Parameters
    ----------
    data_folder : pathlib.Path
        Folder for the figure and pickle
    bb : 3-tuple of 2-tuple
        For each axis, start and end of bounding box
    neuron_name : str
    fig : plt.Figure
    """
    fig.suptitle("Alpha Value vs. Collision Chance for Axons (Green) and Dendrites")
    fig_fname = f"{neuron_name}_coll_vs_alpha_{bb}.png"
    fig.savefig(data_folder / fig_fname, dpi=300, transparent=True)
    

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
    if len(data) < 5:
        g.ax_joint.scatter(data["coll"], data["alpha"], c=color, s=7, alpha=0.6)
    else:
        sns.regplot(data=data, x='coll', y='alpha', color=color, scatter_kws={'s': 7, 'alpha': 0.6}, ax=g.ax_joint)
    _, binx, _ = g.ax_marg_x.hist(data["coll"], alpha=0.6, color=color, bins=bins["x"])
    _, biny, _ = g.ax_marg_y.hist(
        data["alpha"], alpha=0.6, color=color, orientation="horizontal", bins=bins["y"]
    )
    return g, {"x": binx, "y": biny}


def main(neuron_name: str, data_folder: pathlib.Path, blocks: tuple):
    """Main pipeline for this file, handling a single neuron.

    The neuron's graph data is read and then it's divided into blocks and
    analyzed. Each "interesting" block is saved as a figure and inside a 
    pickle file which aggregates the coordinates of the interesting blocks
    of that neuron. These files are written to the "data_folder" location.

    Parameters
    ----------
    neuron_name : str
    data_folder : pathlib.Path
        The location to which the pickle file and figures will be written to
    blocks : 3-tuple of 2-tuple
        Start and end coordinate per axis
    """
    path = pathlib.Path(
        f"/data/neural_collision_detection/results/2020_02_14/graph_{neuron_name}_with_collisions.gml"
    )
    points = load_neuronal_points(path, neuron_name)
    indices, _ = divide_neuron_into_blocks(points.loc[:, "x":"z"], blocks)
    uniques = np.unique(indices)
    blocks = ((points.iloc[indices == unique], data_folder, neuron_name) for unique in uniques)
    with multiprocessing.Pool() as mp:
         mp.starmap(divide_and_plot, blocks)
    # for block in blocks:
    #     divide_and_plot(*block)
    #     plt.show()

    
if __name__ == "__main__":
    data_folder = pathlib.Path("/data/neural_collision_detection/results/for_article/fig2")
    neuron_name = "AP120410_s1c1"
    main(neuron_name, data_folder, (10, 19, 6))


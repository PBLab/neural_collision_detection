"""This module deals with dividing each neuron into sub-block in 3D space.
Once the neuron is divided we can calculate properties of that block.
Properties may include the distribution of alpha shapes, dist. of collisions,
axon-dendrite relations in the block and more.
"""
import pathlib
import multiprocessing
from typing import Tuple, List, Optional
from collections import namedtuple, defaultdict

import numpy as np
import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import zarr

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    CollisionsDistNaive,
)


LMResults = namedtuple("LMResults", "r2, const, slope")


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


def divide_neuron_into_blocks(
    points: pd.DataFrame, blocks=(10, 10, 5)
) -> Tuple[np.ndarray, List[np.ndarray], str]:
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
    block_sizes : str
        Size of blocks in microns per axis
    """
    print(f"blocks: {blocks}")
    bounding_box = find_points_bounding_box(points)
    linspace_per_ax = []
    block_sizes = []
    for minmax, block in zip(bounding_box, blocks):
        bins = np.linspace(
            minmax[0], minmax[1], block + 1, endpoint=True, dtype=np.int32
        )
        linspace_per_ax.append(bins)
        block_sizes.append(str(bins[1] - bins[0]))
        print(f"The size of this block is {bins[1] - bins[0]} microns.")
    ret = scipy.stats.binned_statistic_dd(
        points.to_numpy(), np.arange(len(points)), "count", bins=linspace_per_ax
    )
    block_sizes = "-".join(block_sizes)
    return ret[2], linspace_per_ax, block_sizes


def divide_and_plot(
        all_data: pd.DataFrame, data_folder: pathlib.Path, neuron_name: str, blocksize: str, no_plot: bool = True
) -> Optional[Tuple[tuple, LMResults, LMResults]]:
    """Divides the given data frame into axonal and dendritic blocks
    and plots them together on the same JointPlot.

    The functions tries to deal with situations where there are only axonal points
    and\\or dendritic points.

    It will return a not-None object only if both dendrites and axons
    were present in the same data block.

    Parameters
    ----------
    all_data : pd.DataFrame
        A DF consisting of both axonal and dendritic data with a "type"
        column that separates them.
    data_folder : pathlib.Path
        Folder to write the data into
    neuron_name : str
    blocksize : str
        Size of block in um. Needed for serialization
    no_plot : bool
        Whether to plot the figures and linear models

    Returns
    -------
    tuple, optional
        The bounding box and results for the axon and dendrite of that block
    """
    all_data.loc[:, "is_ax"] = all_data.loc[:, "type"].str.contains("Axon")
    axonal = all_data.query("is_ax == True")
    dendritic = all_data.query("is_ax == False")
    both = 0
    if no_plot:
        if axonal.empty and dendritic.empty:
            return
        else:
            bb = find_points_bounding_box(all_data.loc[:, "x":"z"])
            return bb, (None, None, None), (None, None, None)

    if not axonal.empty:
        g, bins, ax_lmresult = plot_distribution(axonal, color="C2")
        both += 1
    else:
        g = sns.JointGrid(x="alpha", y="coll", data=dendritic)
        bins = None
        ax_lmresult = None
    if not dendritic.empty:
        g, _, dend_lmresult = plot_distribution(dendritic, color="C1", g=g, bins=bins)
        both += 1
    if both == 2:
        bb = find_points_bounding_box(all_data.loc[:, "x":"z"])
        _serialize_fig(data_folder, bb, neuron_name, g.fig)
        return bb, _create_lm_results(ax_lmresult), _create_lm_results(dend_lmresult)


def _default_results_dict() -> dict:
    """Callable that returns a specialized 'data structure'
    for safe-keeping the results of this computation"""
    return {"bounding_boxes": [], "lmresults": []}


def _create_lm_results(
    lmresults: sm.regression.linear_model.RegressionResultsWrapper,
) -> Optional[LMResults]:
    """Helper function create an LMResults instance from the given data.

    Parameters
    ----------
    lmresults : sm.regression.linear_model.RegressionResultsWrapper
        Results of the linear model

    Returns
    -------
    LMResults, optional
        A picklable format, if indeed there were results. Else None
    """
    try:
        return LMResults(lmresults.rsquared, lmresults.params[0], lmresults.params[1])
    except AttributeError:
        return None


def _serialize_fig(
    data_folder: pathlib.Path, bb: tuple, neuron_name: str, fig: plt.Figure
):
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
    fig.suptitle("Collision Chance vs. Alpha Value for Axons (Green) and Dendrites")
    fig_fname = f"{neuron_name}_alpha_vs_coll_{bb}.png"
    fig.savefig(data_folder / fig_fname, dpi=300, transparent=True)


def plot_distribution(data: pd.DataFrame, color, g=None, bins=None) -> Tuple:
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

    Returns
    -------
    g : sns.JointGrid
        The grid seaborn object we're plotting with
    dict
        A dictionary with the ["x"] and ["y"] bins of the histograms
    lmresult : sm.regression.linear_model.RegressionResultsWrapper, optional
        The results of the linear regression
    """
    if not g:
        g = sns.JointGrid(x="alpha", y="coll", data=data)
    if not bins:
        bins = dict(x=None, y=None)
    if len(data) < 5:
        g.ax_joint.scatter(data["alpha"], data["coll"], c=color, s=7, alpha=0.6)
        lmresult = None
    else:
        lmresult = _calc_regression(data)
        _plot_regression(data, color, g.ax_joint, lmresult.rsquared)
    _, binx, _ = g.ax_marg_x.hist(data["alpha"], alpha=0.6, color=color, bins=bins["x"])
    _, biny, _ = g.ax_marg_y.hist(
        data["coll"], alpha=0.6, color=color, orientation="horizontal", bins=bins["y"]
    )
    return g, {"x": binx, "y": biny}, lmresult


def _plot_regression(data: pd.DataFrame, color: str, ax: plt.Axes, rsquared: float):
    """Plots a regression line with the scattered point for the given data.

    This method assumes that statsmodels was already used to calculate the regression
    parameters, and now it merely has to display them (using seaborn).

    Parameters
    ----------
    data : pd.DataFrame
        Data containing the 'alpha' and 'coll' columns
    color : str
        Color of the current plotted points
    ax : plt.Axes
        Axis to draw on
    rsquared : float
        R^2 value
    """
    locations = {"C1": (0.8, 0.9), "C2": (0.8, 0.8)}
    no_nulls = data.dropna()
    sns.regplot(
        data=no_nulls,
        x="alpha",
        y="coll",
        color=color,
        scatter_kws={"s": 7, "alpha": 0.6},
        ax=ax,
    )

    plt.text(
        *locations[color],
        f"$R^2={rsquared:.2f}$",
        horizontalalignment="center",
        figure=ax.figure,
        verticalalignment="center",
        transform=ax.transAxes,
        color=color,
    )


def _calc_regression(
    data: pd.DataFrame,
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """Calculate an ordinary linear regression for the given data.

    Parameters
    ----------
    data : pd.DataFrame
        Alpha shapes and collision chance data

    Returns
    -------
    sm.regression.linear_model.RegressionResultsWrapper
    """
    no_nulls = data.dropna()
    mod = sm.OLS(
        no_nulls["coll"].to_numpy(), sm.add_constant(no_nulls["alpha"].to_numpy())
    )  # y then x
    res = mod.fit()
    return res


def serialize_data(results, neuron_name, data_folder, blocksize):
    """Asserts that a dataset with the given parameters indeed exists on disk
    in the given location.

    Parameters
    ----------
    max_nelem : int
        Number of elements in the array
    blocksize : str
        The current blocksize, as a string
    data_folder : pathlib.Path
        Place to write the data to
    neuron_name : str
    """
    zarr_fname = data_folder / "bb_coord_alpha_coll.zarr"
    data = zarr.open(str(zarr_fname), "a")
    neuron = data.require_group(neuron_name)
    block = neuron.require_group(blocksize)
    bounding_box = block.require_dataset(
        "bounding_boxes", (len(results), 3, 2), dtype=np.float32
    )
    bbs = _extract_bounding_boxes(results)
    bounding_box[:] = bbs
    _insert_lmresults(results, block)


def _extract_bounding_boxes(results):
    bbs = [res[0] for res in results]
    bbs = np.asarray(bbs, dtype=np.float32)
    return bbs


def _insert_lmresults(results, block):
    lmres = block.require_group("lmresults")
    all_axons = _populate_neurite_array(results, 1)
    all_dends = _populate_neurite_array(results, 2)
    for neurite, data in zip(["axon", "dendrite"], [all_axons, all_dends]):
        group = lmres.require_group(neurite)
        r2 = group.require_dataset("r2", len(results), dtype=np.float32)
        r2[:] = data[:, 0]
        const = group.require_dataset("const", len(results), dtype=np.float32)
        const[:] = data[:, 1]
        slope = group.require_dataset("slope", len(results), dtype=np.float32)
        slope[:] = data[:, 2]


def _populate_neurite_array(results, index):
    resulting_array = np.zeros((len(results), 3), dtype=np.float32)
    for idx, res in enumerate(results):
        current_data = res[index]
        if not current_data:
            current_data = [np.nan, np.nan, np.nan]
        resulting_array[idx, :] = current_data[0], current_data[1], current_data[2]
    return resulting_array


def main(neuron_names: List[str], data_folder: pathlib.Path, block_nums: tuple):
    """Main pipeline for this file, handling a single neuron.

    The neuron's graph data is read and then it's divided into blocks and
    analyzed. Each "interesting" block is saved as a figure and inside a
    pickle file which aggregates the coordinates of the interesting blocks
    of that neuron. These files are written to the "data_folder" location.

    Parameters
    ----------
    neuron_names : List[str]
    data_folder : pathlib.Path
        The location to which the pickle file and figures will be written to
    block_nums : 3-tuple
        Number of blocks in each direction
    """
    for neuron_name in neuron_names:
        print(f"Currently processing neuron {neuron_name}...")
        path = pathlib.Path(
            f"/data/neural_collision_detection/results/2020_02_14/graph_{neuron_name}_with_collisions.gml"
        )
        points = load_neuronal_points(path, neuron_name)
        per_block, _, blocksize = divide_neuron_into_blocks(
            points.loc[:, "x":"z"], block_nums
        )
        uniques = np.unique(per_block)
        blocks = (
            (points.iloc[per_block == unique], data_folder, neuron_name, blocksize)
            for unique in uniques
        )
        with multiprocessing.Pool() as mp:
            results = mp.starmap(divide_and_plot, blocks)
        results = [res for res in results if res is not None]
        # results = []
        # for block in blocks:
        #     result = divide_and_plot(*block)
        #     if result:
        #         results.append(result)
        #     # plt.show()
        serialize_data(results, neuron_name, data_folder, blocksize)


if __name__ == "__main__":
    data_folder = pathlib.Path(
        "/data/neural_collision_detection/results/for_article/fig2"
    )
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
    neuron_name = ["AP120410_s3c1"]
    main(neuron_names, data_folder, (30, 57, 18))  # (10, 19, 6) was ~ 30x30x30, (20, 38, 12) was 15-16-16

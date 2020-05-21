"""This module calculates the alpha-shape values for points
which belong to either the dendrite or axon, and tries to find
pairs of nearby axon-dendrite points which are differnet in
their collision numbers or in their alpha shape maximal
value.
"""
import pathlib
import multiprocessing

import scipy.spatial.distance as scidist
import pandas as pd
import numpy as np

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    CollisionsDistNaive,
)


def distance_between_ax_dend(ax: np.ndarray, dend: np.ndarray) -> np.ndarray:
    """Return the distance between each axonal and dendritic point.

    Points are in 3D.

    Parameters
    ----------
    ax, dend : np.ndarray
        3D points

    Returns
    -------
    np.ndarray
        ax by dend array of distances
    """
    return scidist.cdist(ax, dend)


def find_closest_dends_to_ax(
    dist: np.ndarray, ax: pd.DataFrame, dend: pd.DataFrame, num: int = 20
) -> pd.DataFrame:
    """For each axonal points, finds the num closets dendritic points.

    The input is assumed to be arriving from ``distance_between_ax_dend``, so the axons
    should be in the rows, and the dendrites on the columns.

    Parameters
    ----------
    dist : np.ndarray
        Index of axonal point on the rows, and dendritic on the columns.
    ax, dend : pd.DataFrame
        Axonal and dendritic points in "x":"z" columns.
    num : int, optional
        Number of dendritic indices to keep, by default 20

    Returns
    -------
    pd.DataFrame
        A long-form data frame where for each axonal point there are num rows which
        represent the num closest dendritic points.
    """
    closest_dends = np.argsort(dist, axis=1)[:, :num]
    chosen_dends = dend.iloc[closest_dends.ravel()]
    dists = np.take_along_axis(dist, closest_dends, axis=1).ravel()
    chosen_axons = np.kron(np.arange(len(ax)), np.ones(num))
    assert len(chosen_axons) == len(chosen_dends)
    df = pd.DataFrame(
        {
            "ax_x": ax.loc[chosen_axons, "x"].to_numpy(),
            "ax_y": ax.loc[chosen_axons, "y"].to_numpy(),
            "ax_z": ax.loc[chosen_axons, "z"].to_numpy(),
            "ax_row": ax.loc[chosen_axons, "orig_row"].to_numpy(),
            "ax_coll": ax.loc[chosen_axons, "coll"].to_numpy(),
            "dend_x": chosen_dends["x"].to_numpy(),
            "dend_y": chosen_dends["y"].to_numpy(),
            "dend_z": chosen_dends["z"].to_numpy(),
            "dend_row": chosen_dends["orig_row"].to_numpy(),
            "dend_coll": chosen_dends["coll"].to_numpy(),
            "dist": dists,
        }
    )
    df["collision_delta"] = np.abs(df["dend_coll"] - df["ax_coll"])
    return df


def generate_df_from_neuron(fname: pathlib.Path, neuron_name: str) -> pd.DataFrame:
    """Creates a dataframe which contains the neural points and an index values
    hinting whether the point belongs to the axon or the dendrite.

    Parameters
    ----------
    fname : pathlib.Path
        Location of the data
    neuron_name : str
        Name of neuron

    Returns
    -------
    pd.DataFrame
        Axons and dendritic points are labeled separately
    CollisionsDistNaive
        Object containing collisions and graph of neuron
    """
    g = CollisionsDistNaive.from_graph(fname, neuron_name)
    g.run()
    points = g.all_colls.set_index(["type"])
    return points, g


def calc_alpha_shape_diff_between_near_axdends(
    closest: pd.DataFrame, alphas: np.ndarray
):
    """Finds the alpha shape value difference between nearby axons and dends which exhibit
    large difference in collision chance.

    The ``closest`` table contains information on nearby axons and dendrites and their
    different collision probabilities. The goal here is to find the largest differences
    between nearby axons and dendrites and see if the alpha shape values reflect the
    difference in the collision probability.

    Parameters
    ----------
    closest : pd.DataFrame
        For each axon store the X nearby dendrites
    alphas : np.ndarray
        For each point in the neuron the table stores the alpha shape value that was the
        earliest "interior" result of that point.
    """
    top = closest["collision_delta"].quantile(q=0.99)
    top_closest = closest.query("collision_delta > @top")
    top_closest.loc[:, "ax_alpha"] = alphas[top_closest.loc[:, "ax_row"]]
    top_closest.loc[:, "dend_alpha"] = alphas[top_closest.loc[:, "dend_row"]]
    return top_closest


def find_first_interior_alpha_shape_value(alphas: pd.DataFrame) -> np.ndarray:
    """Finds the smallest alpha value that interiorized each point.

    When calculating alpha shapes, each point on the neuron is continuously
    checked for whether it's inside, on the edge, or outside the shape. The functions'
    goal is to detect the "transition" of each point from being on the outside of
    the shape (values of > 0) to being inside (value == 0).

    Parameters
    ----------
    alphas : pd.DataFrame
        Neural points are on the rows and alpha shape values are the columns

    Returns
    -------
    np.ndarray
        The alpha value for each neural point. NaN if it's never found inside
    """
    interior_alphas = np.where(alphas == 0)
    first_zeros = pd.DataFrame({"x": interior_alphas[0], "y": interior_alphas[1]})
    first_alpha = first_zeros.groupby("x").min()
    all_rows = np.full((alphas.shape[0],), np.nan)
    all_rows[first_alpha.index] = alphas.columns[first_alpha["y"]]
    return all_rows


def main_alpha_pipe(neuron_name: str, alphas_folder: pathlib.Path) -> np.ndarray:
    """Pipeline for alpha values normalization.

    This pipeline grants the alpha value for each of the points
    composing the neuron which was the first non-zero one, i.e.
    the lowest alpha value that included the point in the interior
    side of the shape.

    Parameters
    ----------
    neuron_name : str
        Neuron name
    alphas_folder : pathlib.Path
        Location of the alpha shape results

    Returns
    -------
    np.ndarray
        Alpha value per point of the neuron
    """
    alphas_fname = alphas_folder / f"{neuron_name}_alpha_distrib.h5"
    alphas = pd.read_hdf(alphas_fname, "data")
    alpha_per_point = find_first_interior_alpha_shape_value(alphas)
    return alpha_per_point


def main_collisions_pipe(
    neuron_name: str, results_folder: pathlib.Path
) -> pd.DataFrame:
    """Pipeline for collision data processing.

    This pipeline processes the collision data by looking at nearby pairs
    of axons and dendrites. It creates a long-form dataframe that contains
    a row per axon-dendrite pair, where each axon has ``num`` clode dends
    to it.

    Parameters
    ----------
    neuron_name : str
        Name of neuron
    results_folder : pathlib.Path
        Folder with neuronal data

    Returns
    -------
    pd.DataFrame
        A table of axonal-dendritic pairs with the data about their proximity
        and collision chances
    """
    collisions_fname = results_folder / f"graph_{neuron_name}_with_collisions.gml"
    points, g = generate_df_from_neuron(collisions_fname, neuron_name)
    all_collisions_ax = g.parsed_axon.loc[:, ["coll", "x", "y", "z"]]
    all_collisions_dend = g.parsed_dend.loc[:, ["coll", "x", "y", "z"]]
    dist = distance_between_ax_dend(
        all_collisions_ax.loc[:, "x":"z"].to_numpy(),
        all_collisions_dend.loc[:, "x":"z"].to_numpy(),
    )
    closest_dend = find_closest_dends_to_ax(dist, g.parsed_axon, g.parsed_dend)
    return closest_dend


def main(neuron_name: str, results_folder: pathlib.Path, alphas_folder: pathlib.Path):
    """Main pipeline for correlating collisions and alpha values on the same neuron.

    For each neuron, we take the collision data and the alpha shape values data,
    which were both calculated separately, and we try to "correlate" them by finding
    nearby pairs of axons and dendrites which exhibit different collisions chances.
    For each of these pairs we look at the alpha shape differene and see if the alpha
    shape can explain such behavior.

    The pipeline writes to disk HDF5 dataframes with the data gathered here.

    Parameters
    ----------
    neuron_name : str
        Name of the neuron
    results_folder : pathlib.Path
        Path containing neuronal data
    alphas_folder : pathlib.Path
        Path containing alpha shapes results
    """
    print(neuron_name)
    alpha_per_point = main_alpha_pipe(neuron_name, alphas_folder)
    closest_dend = main_collisions_pipe(neuron_name, results_folder)
    top_closest = calc_alpha_shape_diff_between_near_axdends(
        closest_dend, alpha_per_point
    )
    top_closest = top_closest.dropna()
    top_closest.to_hdf(alphas_folder / f"{neuron_name}_closest_pairs.h5", "data")


if __name__ == "__main__":
    results_folder = pathlib.Path("/data/neural_collision_detection/results/2020_02_14")
    alphas_folder = pathlib.Path(
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
    args = ((neuron, results_folder, alphas_folder) for neuron in neuron_names)
    with multiprocessing.Pool() as mp:
        mp.starmap(main, args)

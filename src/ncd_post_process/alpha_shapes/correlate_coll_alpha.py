"""
This module contains functions that analyze the results of the alpha shape
calculations as they were written to disk. This is done in the "main_per_neuron"
function, which runs in parallel over all of them and collects the fitting
results.

You're then able to use the "aggregate_and_plot_all_results" function to 
generate a collision_vs_alpha_linear(log)_fit.csv file that contains the data
per neuron per type on the offset and slope, as well as the figure which
aggregates all of these results into one publishable figure.

This module also contains the "analyze_pairs" function which reads
these HDF files and analyzes them in a scatterplot.
"""
import multiprocessing
import pathlib
from itertools import chain
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.optimize

from ncd_post_process.alpha_shapes.distance_alpha import generate_df_from_neuron


neuron_names = {
    "AP120410_s1c1": "V",
    "AP120410_s3c1": "V",
    "AP120412_s3c2": "V",
    "AP120416_s3c1": "IV",
    "AP120419_s1c1": "VI",
    "AP120420_s1c1": "IV",
    "AP120420_s2c1": "II/III",
    # "AP120507_s3c1": "II/III",
    "AP120510_s1c1": "II/III",
    # "AP120522_s3c1": "I",  # ?
    "AP120524_s2c1": "II/III",
    "AP120614_s1c2": "V",
    "AP130312_s1c1": "II/III",
    # "AP131105_s1c1": "II/III",  # ?
}


def analyze_pairs(foldername: pathlib.Path):
    """Aggregates all pairs into one scatterplot"""
    all_pairs_files = foldername.glob("*closest_pairs.h5")
    dfs = []
    for file in all_pairs_files:
        data = pd.read_hdf(file, key="data_single_pair")
        relevant_columns = data.loc[:, ["collision_delta", "alpha_delta"]]
        relevant_columns.loc[:, "name"] = file.name
        dfs.append(relevant_columns)
    dfs: pd.DataFrame = pd.concat(dfs)  # type: ignore
    quant_high = dfs.loc[:, "alpha_delta"].quantile(0.99)
    dfs = dfs.loc[dfs["alpha_delta"] < quant_high, :]
    ax = sns.regplot(data=dfs, x="alpha_delta", y="collision_delta")
    ax.set_xscale("log")
    return dfs


def _apply_layer_to_neuron_name(name):
    return "II/III" if neuron_names[name] == 'II/III' else "IV-VI"


def scatter_coll_vs_alpha_for_all_points(
    points: pd.DataFrame, results_dir: pathlib.Path, neuron_name: str, fit_result: dict
):
    """Scatters collisions vs alpha value for all points of a given neuron.

    Each neurite is in its own panel, and the fitting results (the intercept
    and slope of a linear model) are plotted over the scatterplot.

    Parameters
    ----------
    points : pd.DataFrame
        Data with "alpha" and "coll" columns and "type" in the index
    results_dir : pathlib.Path
        Directory to save results
    neuron_name : str
    fit_result : dict of 2-tuples
        For each neurite (str key) a 2-tuple of (offset, slope)
    """
    print(neuron_name)
    color_palette = ["C2"] + ["C1"] * (
        len(fit_result) - 1
    )  # all dendrites will be orange, the axon is green
    hue_order = ['Axon0'] + [f'Dendrite{num}' for num in range(1, len(fit_result))]
    ax = sns.relplot(
        data=points.reset_index().sample(frac=0.3),
        x="alpha",
        y="coll",
        col="type",
        hue="type",
        hue_order=hue_order,
        kind='scatter',
        col_wrap=2,
        palette=color_palette,
    )
    for a, neurite_name in zip(ax.axes, fit_result):
        a.set_xscale("log")
        x = points.query("type == @neurite_name").loc[:, "alpha"].to_numpy()
        a.plot(
            x,
            linear_model(x, fit_result[neurite_name][0], fit_result[neurite_name][1]),
            "k-.",
        )

    ax.savefig(
        results_dir / f"{neuron_name}_coll_vs_alpha_all_points.pdf",
        transparent=True,
        dpi=300,
    )


def linear_model(x: np.ndarray, a0: float, a1: float):
    """Linear model to minimize.

    Parameters
    ----------
    x : np.ndarray
        Time vector
    a0 : float
        Offset
    a1 : float
        Slope
    """
    return a0 + a1 * np.log(x)


def fit(x: np.ndarray, y: np.ndarray) -> tuple:
    """Runs the linear_model fit on the given data.

    Parameters
    ----------
    x, y : np.ndarray
        Independent and dependent variables

    Returns
    -------
    2-tuple
       Offset in [0], slope in [1]
    """
    res_lsq, _ = scipy.optimize.curve_fit(
        linear_model, x, y, p0=(0, 0), method="trf", loss="soft_l1", max_nfev=100_000
    )
    return res_lsq


def fit_subset_of_points(points: pd.DataFrame, neuron_name: str) -> dict:
    """Calculate the curve fit for each type of points in the data.

    The types are the axon and all dendrites, and the fit is
    calculated separately.

    Parameters
    ----------
    points : pd.DataFrame
        Data with coll, alpha and type columns
    neuron_name : str

    Returns
    -------
    dict
        For each neurite (key) a 2-tupe of (offset, slope)
    """
    neuronal_fitting_data = {}
    for label, data in points.groupby("type"):
        x = data.loc[:, "alpha"].to_numpy()
        y = data.loc[:, "coll"].to_numpy()
        result = fit(x, y)
        neuronal_fitting_data[label] = result
    return neuronal_fitting_data


def convert_result_to_dataframe(data: dict):
    neurite_type = [[k, r.keys()] for k, r in data.items()]
    neuron_name = []
    for item in neurite_type:
        neuron_name.append(list(item[0] for _ in item[1]))
    neuron_name = list(chain.from_iterable(neuron_name))
    neurite_type = list(chain.from_iterable([item[1] for item in neurite_type]))
    assert len(neuron_name) == len(neurite_type)
    multiindex = pd.MultiIndex.from_tuples(
        list(zip(*[neuron_name, neurite_type])), names=["neuron", "type"]
    )
    df = pd.DataFrame(index=multiindex, columns=["offset", "slope"])

    for key, val in data.items():
        for typ, vals in val.items():
            df.loc[(key, typ), :] = vals
    return df


def add_axon_id_to_results(df: pd.DataFrame) -> pd.DataFrame:
    """Adds an "is_axon" columns to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    df["is_axon"] = False
    df.loc[pd.IndexSlice[:, "Axon0"], "is_axon"] = True
    return df


def add_normed_values_to_results(
    df: pd.DataFrame, points_list: Iterable
) -> pd.DataFrame:
    """Adds normed_offset and normed_slope columns to the data.

    The normalization is based on the topological length of each of
    the neuritic trees.

    Parameters
    ----------
    df : pd.DataFrame
    points_list : Iterable
        Points of every neuron sorted by the neurite it belongs to.
        The entry in each item is the neuron name, the second is a
        DataFrame with the data.

    Returns
    -------
    pd.DataFrame
    """
    df["normed_offset"] = 0.0
    df["normed_slope"] = 0.0
    for name, points in points_list:
        maxs = points.groupby("type").max()
        df.loc[name, "normed_offset"] = (
            df.loc[name, "offset"] / maxs["dist"]
        ).to_numpy()
        df.loc[name, "normed_slope"] = (df.loc[name, "slope"] / maxs["dist"]).to_numpy()
    return df


def main_per_neuron(
    neuron_name: str, neuron_graph_folder: pathlib.Path, save_folder: pathlib.Path
) -> tuple:
    """Calculate a neuron's coll vs alpha distribution parameters.

    The function plots the distribtion of collisions vs alpha value
    for the given neuron, saves that figure, and the runs a linear
    curve fitting algorithm to extract the offset and slope of that
    curve.

    Parameters
    ----------
    neuron_name : str
    neuron_graph_folder : pathlib.Path
    save_folder : pathlib.Path

    Returns
    -------
    2-tuple
        Name and (offset, slope)
    """
    collisions_fname = neuron_graph_folder / f"graph_{neuron_name}_with_collisions.gml"
    points, _ = generate_df_from_neuron(collisions_fname, neuron_name)
    points = points.dropna()
    result = fit_subset_of_points(points, neuron_name)
    scatter_coll_vs_alpha_for_all_points(points, save_folder, neuron_name, result)
    return neuron_name, result, points


def aggregate_and_plot_all_results(results: list, folder: pathlib.Path) -> pd.DataFrame:
    """Aggregates the per-neuron results into a single figure
    which compares the intercept and slope of the fitted lines
    between the two groups of neurons.

    Parameters
    ----------
    results : list
        Saves the neuron name, fitting results and DF of each neuron
    folder : pathlib.Path
        Folder in which to save
    Returns
    -------
    data_as_df : pd.DataFrame
        The data in a melted dataframe format
    """
    curve_fit_results = {name: res for name, res, _ in results}
    data_as_df = convert_result_to_dataframe(curve_fit_results)
    data_as_df = add_axon_id_to_results(data_as_df)
    data_as_df = add_normed_values_to_results(
        data_as_df, ((res[0], res[2]) for res in results)
    )
    data_as_df = data_as_df.reset_index().melt(
        id_vars=["neuron", "type", "is_axon"],
        value_vars=["offset", "slope", "normed_offset", "normed_slope"],
        var_name="parameter",
    )
    data_as_df.loc[:, 'layer'] = data_as_df.neuron.apply(_apply_layer_to_neuron_name)
    data_as_df.to_csv(folder / "collision_vs_alpha_log_fit.csv")
    ax = sns.catplot(
        data=data_as_df,
        x="layer",
        y="value",
        hue="is_axon",
        col="parameter",
        sharey=False,
        size="layer",
        palette=['C1', 'C2'],
    )
    ax.savefig(
        folder / "collision_vs_alpha_log_fit_agg_result.pdf",
        transparent=True,
        dpi=300,
    )
    plt.show()
    return data_as_df


if __name__ == "__main__":
    results_folder = pathlib.Path("/data/neural_collision_detection/results/2020_02_14")
    alphas_folder = pathlib.Path(
        "/data/neural_collision_detection/results/for_article/fig2"
    )
    args = ((name, results_folder, alphas_folder) for name in neuron_names)
    with multiprocessing.Pool() as mp:
        results = mp.starmap(main_per_neuron, args)
    # for neuron in neuron_names:
    #     _, result = main(neuron, results_folder, alphas_folder)
    #     data[neuron] = result
    # data_as_ df = aggregate_and_plot_all_results(results, alphas_folder)

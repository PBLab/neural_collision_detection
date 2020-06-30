"""
This module contains functions that analyze the results of the alpha shape
calculations as they were written to disk.

It generated a collision_vs_alpha_linear_fit.csv file that contains the data
per neuron per type on the offset and slope. The actual generation was done
in an IPython session, this file generated a pickle with the same name.

This module also contains the "analyze_pairs" function which reads
these HDF files and analyzes them in a scatterplot.
"""
import multiprocessing
import pickle
import pathlib
from itertools import chain

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.optimize

from ncd_post_process.alpha_shapes.distance_alpha import generate_df_from_neuron


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


def analyze_pairs(foldername: pathlib.Path):
    """Aggregates all pairs into one scatterplot"""
    all_pairs_files = foldername.glob('*closest_pairs.h5')
    dfs = []
    for file in all_pairs_files:
        data = pd.read_hdf(file, key='data_single_pair')
        relevant_columns = data.loc[:, ['collision_delta', 'alpha_delta']]
        relevant_columns.loc[:, 'name'] = file.name
        dfs.append(relevant_columns)
    dfs: pd.DataFrame = pd.concat(dfs)  # type: ignore
    quant_high = dfs.loc[:, "alpha_delta"].quantile(0.99)
    dfs = dfs.loc[dfs["alpha_delta"] < quant_high, :]
    ax = sns.regplot(data=dfs, x='alpha_delta', y='collision_delta')
    ax.set_xscale('log')
    return dfs


def scatter_coll_vs_alpha_for_all_points(points: pd.DataFrame, results_dir: pathlib.Path, neuron_name: str):
    """Scatters collisions vs alpha value for all points of a given neuron.

    Parameters
    ----------
    points : pd.DataFrame
        Data with "alpha" and "coll" columns and "type" in the index
    results_dir : pathlib.Path
        Directory to save results
    neuron_name : str
    """
    print(neuron_name)
    ax = sns.relplot(data=points.reset_index(), x='alpha', y='coll', col='type', col_wrap=2, alpha=0.7)
    [a.set_xscale('log') for a in ax.axes]
    ax.savefig(results_dir / f'{neuron_name}_coll_vs_alpha_all_points.pdf', transparent=True, dpi=300)


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
    return a0 + a1 * x


def fit(x, y):
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
    res_lsq, _ = scipy.optimize.curve_fit(linear_model, x, y, p0=(0, 0), method='trf', loss='soft_l1', max_nfev=100_000)
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
    for label, data in points.groupby('type'):
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
    multiindex = pd.MultiIndex.from_tuples(list(zip(*[neuron_name, neurite_type])), names=['neuron', 'type'])
    df = pd.DataFrame(index=multiindex, columns=["offset", "slope"])

    for key, val in data.items():
        for typ, vals in val.items():
            df.loc[(key, typ), :] = vals
    df = df.reset_index().melt(id_vars=['neuron', 'type', 'is_axon'], value_vars=['offset', 'slope'], var_name='parameter')
    return df


def main(neuron_name: str, neuron_graph_folder: pathlib.Path, save_folder: pathlib.Path) -> tuple:
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
    scatter_coll_vs_alpha_for_all_points(points, save_folder, neuron_name)
    result = fit_subset_of_points(points, neuron_name)
    return neuron_name, result


if __name__ == '__main__':
    results_folder = pathlib.Path("/data/neural_collision_detection/results/2020_02_14")
    alphas_folder = pathlib.Path(
        "/data/neural_collision_detection/results/for_article/fig2"
    )
    data = {}  # will hold curve-fitting results
    args = ((name, results_folder, alphas_folder) for name in neuron_names)
    with multiprocessing.Pool() as mp:
        results = mp.starmap(main, args)
    for name, res in results:
        data[name] = res
    # for neuron in neuron_names:
    #     _, result = main(neuron, results_folder, alphas_folder)
    #     data[neuron] = result
    data_as_df = convert_result_to_dataframe(data)
    data_as_df.to_csv(alphas_folder / 'collision_vs_alpha_linear_fit.csv')
    ax = sns.catplot(data=data_as_df, x='is_axon', y='value', hue="type", col="parameter", sharey=False); ax.axes[0][0].set_yscale('log'); ax.axes[0][1].set_yscale('log'); plt.show()

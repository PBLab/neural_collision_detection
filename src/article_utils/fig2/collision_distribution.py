"""This file generates a figure with 4 axes showing the collision distribution
as a function of the distance from the main axis of the neuron to each of the 3
axes (x, y, z), with the fourth subplot showing the collision chance as a function
of the distance to the soma.
"""
import pathlib
import multiprocessing

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    CollisionsDistNaive,
)

neuron_names = [
        # "AP120410_s1c1",
        # "AP120410_s3c1",
        # "AP120412_s3c2",
        # "AP120416_s3c1",
        # "AP120419_s1c1",
        # "AP120420_s1c1",
        # "AP120420_s2c1",
        # "AP120507_s3c1",
        # "AP120510_s1c1",
        "AP120522_s3c1",
        # "AP120523_s2c1",
        # "AP120524_s2c1",
        # "AP120614_s1c2",
        # "AP130110_s2c1",
        # "AP130312_s1c1",
        # "AP130606_s2c1",
        # "AP131105_s1c1",
        # "MW120607_LH3",
]

palette = ["C2", "C1", "C3", "C8", "C4", 'C0', 'C5']


def compute_dist_to_origin(df: pd.DataFrame):
    """Calculates the distance to the origin (cell body) for each collision."""
    dists = np.sqrt(df.loc[:, "x"] ** 2 + df.loc[:, "y"] ** 2 + df.loc[:, "z"] ** 2)
    return dists


def plot_colls_distance_correlation(folder: pathlib.Path, neuron_name: str) -> CollisionsDistNaive:
    """Shows the correlation of the given neuron's collision numbers
    to the distance from both the origin and the rest of the axes.

    Parameters
    ----------
    folder : pathlib.Path
        The folder that the data is located at, and to which the resulting
        figure will be written to.
    neuron_name : str

    Returns
    -------
    g : CollisionsDistNaive
        Graph object of the neuron
    """
    fname = folder / f"graph_{neuron_name}_with_collisions.gml"
    if not fname.exists():
        return
    g = CollisionsDistNaive.from_graph(fname, neuron_name)
    g.run()
    g.all_colls["dist_to_origin"] = compute_dist_to_origin(g.all_colls)
    g.all_colls["z_abs"] = g.all_colls["z"].abs()
    g.all_colls["y_abs"] = g.all_colls["y"].abs()
    g.all_colls["x_abs"] = g.all_colls["x"].abs()
    num_elems = len(g.all_colls["type"].cat.categories)
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    print(neuron_name)
    try:
        sns.scatterplot(
            data=g.all_colls,
            x="z_abs",
            y="coll",
            hue="type",
            palette=palette[:num_elems],
            alpha=0.4,
            ax=axes[0, 0],
        )
        sns.scatterplot(
            data=g.all_colls,
            x="y_abs",
            y="coll",
            hue="type",
            palette=palette[:num_elems],
            alpha=0.4,
            ax=axes[0, 1],
        )
        sns.scatterplot(
            data=g.all_colls,
            x="x_abs",
            y="coll",
            hue="type",
            palette=palette[:num_elems],
            alpha=0.4,
            ax=axes[1, 0],
        )
        sns.scatterplot(
            data=g.all_colls,
            x="dist_to_origin",
            y="coll",
            hue="type",
            palette=palette[:num_elems],
            alpha=0.4,
            ax=axes[1, 1],
        )
        fig.tight_layout()
        fig.savefig(
            str(folder / f"{neuron_name}_all_collisions_vs_distances.png"),
            transparent=True,
            dpi=300,
        )
    except ValueError as e:
        print(f"{neuron_name} had a ValueError: {e}")
    return g


if __name__ == "__main__":
    results_folder = pathlib.Path("/data/neural_collision_detection/results/2020_07_29")
    args = ((results_folder, name) for name in neuron_names)
    with multiprocessing.Pool() as pool:
        pool.starmap(plot_colls_distance_correlation, args)

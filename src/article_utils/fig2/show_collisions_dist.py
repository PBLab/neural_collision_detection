"""
This file contains a few different methods to show the collision distribution
of the different neurons.
The first is by summing up the number of collisions that occurred until a
certain distance and plots it.

The second shows the running average of each neuron's collisions.
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    plot_running_avg_for_all,
)

colors = {"II/III": "C0", "I/IV/V/VI": "C1"}


def _prep_data():
    return plot_running_avg_for_all()[-1]


def plot_collisions_cumsum():
    """Show the cumulative sum of the collisions
    of each neuron.
    """
    data = _prep_data()

    fg = sns.relplot(
        data=data,
        x="dist",
        y="cumsum",
        col="layer",
        hue="type",
        row="name",
        kind="line",
        palette={"Axon": "C2", "Dendrite": "C1"},
    )


def plot_collisions_rolling_avg():
    """Shows the running average of each mouse's collision
    data."""
    data = _prep_data()

    fg = sns.relplot(
        data=data,
        x="dist",
        y="avg_coll",
        col="layer",
        hue="type",
        row="name",
        kind="line",
        palette={"Axon": "C2", "Dendrite": "C1"},
    )


if __name__ == "__main__":
    plot_collisions_rolling_avg()
    plt.show()

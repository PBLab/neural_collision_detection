import pathlib
import enum

import attr
from attr.validators import instance_of
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from find_branching_density import BranchDensity
from ncd_post_process.graph_parsing import load_neuron
from ncd_post_process.analyze_graph import graph_file_to_graph_object


class PlottingOptions(enum.Enum):
    HIST = "hist"
    JOINTPLOT = "joint"


@attr.s
class BranchDensityAndCollisions:
    """
    Takes a generated BranchDensity object and a serialized neuron and compares
    the branching density of that neuron as computed in the BranchDensity class
    with the number of collisions each point on the neuronal tree has. Finally
    it also plots the result.
    """

    bdens = attr.ib(validator=instance_of(BranchDensity))
    graph = attr.ib(validator=instance_of(nx.Graph))
    counts = attr.ib(init=False)

    def main(self, plot=True):
        """ Main pipeline """
        self.counts = self._get_counts_from_bdens()
        self._pop_counts_with_colls()
        if plot:
            self.plot_colls_and_dens()

    def get_top_colls_percentile(self, perc=90) -> np.ndarray:
        """
        Extracts only the topmost ``perc`` percentile of the collision
        data to disk, so that it can later be visualized in Blender
        or by a different method.

        :param int perc: The percentile of data to keep. For example,
        90 means to keep the top 10%.
        """
        self.counts = self._get_counts_from_bdens()
        self._pop_counts_with_colls()
        numeric_perc = self.counts["collisions"].quantile(perc / 100)
        if not numeric_perc > 0.0:
            return np.array([])
        coords = (
            self.counts.loc[self.counts.loc[:, "collisions"] >= numeric_perc, :]
            .reset_index()
            .loc[:, "x":"z"]
            .to_numpy()
        )
        return coords

    def _get_counts_from_bdens(self):
        """
        Runs the main analysis pipeline of the BranchDensity class to
        receive a DataFrame containing the density data per radius.
        :return pd.DataFrame:
        """
        counts = self.bdens.main()
        return counts

    def _pop_counts_with_colls(self):
        self.counts["collisions"] = 0
        row_idx = 0
        for node in self.graph.nodes():
            self.counts.iloc[row_idx, -1] = node.collisions
            row_idx += 1

    def _prepare_colls_dens_data(self, r=10):
        """
        Pre-processing steps before populating the histogram of
        collisions to density.
        """
        axon_idx = self.counts.index.get_level_values("tree") == "Axon"
        axon_df = self.counts.loc[axon_idx]
        dend_df = self.counts.loc[~axon_idx]
        # Divide by 100k due to total number of locations per point. We want the y-axis
        # units to be probability. The 100k number stems from the fact that currently
        # we have 10k points per cortical layer, and we save the 10 best orientations
        # in that location.
        normed_axon = axon_df["collisions"] / 100_000
        normed_dend = dend_df["collisions"] / 100_000
        dens_axon = axon_df[r]
        dens_dend = dend_df[r]
        return normed_axon, normed_dend, dens_axon, dens_dend

    def plot_colls_dens_hist(self, ax=None):
        normed_axon, normed_dend, dens_axon, dens_dend = self._prepare_colls_dens_data()
        if ax is None:
            fig, ax = plt.subplots()

        ax.scatter(dens_axon, normed_axon, c="C2", s=0.2, alpha=0.8, label="Axon")
        ax.scatter(dens_dend, normed_dend, c="C2", s=0.2, alpha=0.8, label="Dendrite")
        ax.set_xlabel(f"U(r={r})")
        ax.set_ylabel("P(collision)")
        ax.legend()
        ax.set_title(
            f"Collisions as a function of density for a single neuron with r={r} um"
        )

    def plot_colls_dens_jointplot(self, neuron_name=None):
        """
        Uses the populated DataFrame from "_pop_counts_with_colls" to plot
        the correlation between number of collisions and the density of each
        point.
        :return:
        """
        r = 10
        normed_axon, normed_dend, dens_axon, dens_dend = self._prepare_colls_dens_data(
            r=r
        )
        rect_scatter, rect_histx, rect_histy = self._set_fig_limits()
        fig = plt.figure(figsize=(8, 8))
        ax_scatter = fig.add_axes(rect_scatter)
        ax_scatter.tick_params(direction="in", top=True, right=True)
        ax_histx = fig.add_axes(rect_histx)
        ax_histx.tick_params(direction="in", labelbottom=False)
        ax_histy = fig.add_axes(rect_histy)
        ax_histy.tick_params(direction="in", labelleft=False)

        ax_scatter.scatter(
            dens_axon, normed_axon, c="C2", s=0.2, alpha=0.8, label="Axon"
        )
        ax_scatter.scatter(
            dens_dend, normed_dend, c="C1", s=0.2, alpha=0.8, label="Dendrite"
        )

        ax_histx.hist([dens_axon, dens_dend], color=["C2", "C1"], bins=50)
        ax_histy.hist(
            [normed_axon, normed_dend],
            color=["C2", "C1"],
            orientation="horizontal",
            bins=50,
        )

        ax_histx.set_xlim(ax_scatter.get_xlim())
        ax_histy.set_ylim(ax_scatter.get_ylim())

        ax_scatter.set_xlabel(f"U(r={r})")
        ax_scatter.set_ylabel("P(collision)")
        ax_scatter.legend()
        fig.suptitle(
            f"Collisions as a function of density for a single neuron {neuron_name} with r={r} um"
        )

    def _set_fig_limits(self):
        """ Helper to create scatter plot limits """
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        spacing = 0.005
        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom + height + spacing, width, 0.2]
        rect_histy = [left + width + spacing, bottom, 0.2, height]
        return rect_scatter, rect_histx, rect_histy


def run_multiple_neurons():
    """
    Creates a 2x2 scatter plot of four collisions-to-density
    comparisons from four different neurons.
    """
    neuron_names = ["AP120410_s3c1", "AP120412_s3c2", "AP120410_s1c1", "AP120416_s3c1"]
    fig, axes = plt.subplots(2, 2)
    for neuron_name, ax in zip(neuron_names, axes.flatten()):
        bdens_coll.main(plot=False)
        bdens_coll.plot_colls_dens_hist(ax)
        ax.set_title(neuron_name)

    fig.suptitle(
        f"Collisions as a function of density for a single neuron with r={10} um"
    )
    plt.show()


def run_single_neuron_with_jointplot():
    """
    Creates a single collisions-to-density jointplot, i.e. a scatter
    plot with the histograms of the two axes on its sides.
    """
    neuron_names = [
        "AP120410_s3c1",
        "AP120412_s3c2",
        "AP120410_s1c1",
        "AP120416_s3c1",
        "AP120419_s1c1",
        "AP120420_s1c1",
        "AP120420_s2c1",
        "AP120507_s3c1",
        "AP120510_s1c1",
        "AP120522_s3c1",
        "AP120524_s2c1",
        "AP120614_s1c2",
        "AP130312_s1c1",
        "AP131105_s1c1",
    ]
    for neuron_name in neuron_names:
        bdens_coll = _instantiate_bdens(neuron_name)
        bdens_coll.main(plot=False)
        bdens_coll.plot_colls_dens_jointplot(neuron_name)
    plt.show()


def _instantiate_bdens(neuron_name):
    """
    Helper method to instantiate a BranchDensity instance,
    as well as a BranchDensityAndCollisions instance.
    """
    neuron_fname = (
        pathlib.Path(__file__).resolve().parents[3]
        / "data"
        / "neurons"
        / f"{neuron_name}.xml"
    )
    py3dn_folder = pathlib.Path(__file__).resolve().parents[2] / "py3DN"
    bdens = BranchDensity(neuron_fname, py3dn_folder)
    neuron_graph = (
        pathlib.Path(__file__).resolve().parents[3]
        / "results"
        / "2019_2_10"
        / f"graph_{neuron_name}_with_collisions.gml"
    )
    try:
        graph = graph_file_to_graph_object(neuron_graph)
    except FileNotFoundError:
        return
    bdens_coll = BranchDensityAndCollisions(bdens, graph)
    return bdens_coll


def run_single_neuron_with_quantile():
    neuron_names = [
        # "AP120410_s3c1",
        # "AP120412_s3c2",
        # "AP120410_s1c1",
        # "AP120416_s3c1",
        # "AP120419_s1c1",
        # "AP120420_s1c1",
        # "AP120420_s2c1",
        # "AP120507_s3c1",
        # "AP120510_s1c1",
        # "AP120522_s3c1",
        # "AP120524_s2c1",
        # "AP120614_s1c2",
        # "AP130312_s1c1",
        "AP131105_s1c1",
    ]
    perc = 90
    for neuron_name in neuron_names:
        bdens_coll = _instantiate_bdens(neuron_name)
        if not bdens_coll:
            continue
        colls = bdens_coll.get_top_colls_percentile(perc)
        fname = (pathlib.Path(__file__).resolve().parents[3]
            / "results"
            / "2019_2_10"
            / f"top_{100-perc}p_likely_colls_{neuron_name}.npy"
        )
        np.save(fname, colls)


if __name__ == "__main__":
    # run_multiple_neurons()
    # run_single_neuron_with_jointplot()
    run_single_neuron_with_quantile()

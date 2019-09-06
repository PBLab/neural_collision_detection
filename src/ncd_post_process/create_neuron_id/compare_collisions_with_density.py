import pathlib
import enum
from typing import Union

import attr
from attr.validators import instance_of
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
import numpy as np
import pandas as pd
import scipy.fftpack
import scipy.spatial.distance

from find_branching_density import BranchDensity
from ncd_post_process.graph_parsing import load_neuron
from ncd_post_process.analyze_graph import graph_file_to_graph_object

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


class PlottingOptions(enum.Enum):
    HIST = "hist"
    JOINTPLOT = "joint"


class NeuronType(enum.Enum):
    AXON = "Axon"
    DENDRITE = "Dendrite"


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
    r = attr.ib(default=10, validator=instance_of(int))
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

    def _prepare_colls_dens_data(self):
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
        dens_axon = axon_df[self.r]
        dens_dend = dend_df[self.r]
        return normed_axon, normed_dend, dens_axon, dens_dend

    def plot_colls_dens_hist(self, ax=None):
        normed_axon, normed_dend, dens_axon, dens_dend = self._prepare_colls_dens_data()
        if ax is None:
            fig, ax = plt.subplots()

        ax.scatter(dens_axon, normed_axon, c="C2", s=0.2, alpha=0.8, label="Axon")
        ax.scatter(dens_dend, normed_dend, c="C2", s=0.2, alpha=0.8, label="Dendrite")
        ax.set_xlabel(f"U(r={self.r})")
        ax.set_ylabel("P(collision)")
        ax.legend()
        ax.set_title(
            f"Collisions as a function of density for a single neuron with r={self.r} um"
        )

    def plot_colls_dens_jointplot(self, neuron_name=None):
        """
        Uses the populated DataFrame from "_pop_counts_with_colls" to plot
        the correlation between number of collisions and the density of each
        point.
        :return:
        """
        normed_axon, normed_dend, dens_axon, dens_dend = self._prepare_colls_dens_data()
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

        ax_scatter.set_xlabel(f"U(r={self.r})")
        ax_scatter.set_ylabel("P(collision)")
        ax_scatter.legend()
        fig.suptitle(
            f"Collisions as a function of density for a single neuron {neuron_name} with r={self.r} um"
        )
        fig.savefig(
            f"results/2019_2_10/colls_density_jointplot_r_{self.r}_{neuron_name}.pdf",
            transparent=True,
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


@attr.s
class BranchDensityAndDist:
    """Takes a generated BranchDensity object and a serializd neuron
    and compares the branching density of that neuron with the
    topological distance in each point of the neuron.
    """

    bdens = attr.ib(validator=instance_of(BranchDensity))
    graph = attr.ib(validator=instance_of(nx.Graph))
    r = attr.ib(default=10, validator=instance_of(int))
    window = attr.ib(default=10, validator=instance_of(int))
    ur = attr.ib(init=False)
    color = attr.ib(init=False)
    topodist_ax = attr.ib(init=False)
    topodist_dend = attr.ib(init=False)
    eucdist_ax = attr.ib(init=False)
    eucdist_dend = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.color = {NeuronType.AXON: "C2",
        NeuronType.DENDRITE: "C1"}

    def main(self, plot=True):
        self.ur = self._get_density_from_bdens()
        fig_topodist, ax_topodist = plt.subplots()
        fig_fft, ax_fft = plt.subplots()
        self.topodist_axon, self.topodist_dend = self._get_topodist_from_graph()
        self.pipeline_for_one(self.topodist_axon, ax_topodist, ax_fft, NeuronType.AXON)
        self.pipeline_for_one(self.topodist_dend, ax_topodist, ax_fft, NeuronType.DENDRITE)
        ax_topodist.legend(["Axon", "Dendrite"])
        ax_fft.legend(["Axon", "Dendrite"])
        fig_topodist.savefig(
            f"results/2019_2_10/density_topodist_r_{self.r}_{self.bdens.neuron_fname.stem}.pdf",
            transparent=True,
        )
        fig_fft.savefig(
            f"results/2019_2_10/density_topodist_fft_r_{self.r}_{self.bdens.neuron_fname.stem}.pdf",
            transparent=True,
        )

    def pipeline_for_one(self, topodist, ax_topodist, ax_fft, neuron_type):
        """
        The entirety of the processing pipeline for a single neuron type -
        The axon or the dendrite.
        """
        nonzero = self._get_nonzero_points_on_tree(topodist)
        self._plot_ur_topo(ax_topodist, topodist, nonzero, neuron_type)
        full_ur = self._conform_ur_to_new_idx(topodist[nonzero], self.ur[self.r].iloc[nonzero])
        avg = full_ur.rolling(window=self.window).mean().dropna()
        x, y = self._fft_ur(avg, sample_freq=self.window)
        self._plot_fft(x, y, ax_fft, neuron_type)

    def _get_density_from_bdens(self):
        """
        Runs the main analysis pipeline of the BranchDensity class to
        receive a DataFrame containing the density data per radius.
        :return pd.DataFrame:
        """
        counts = self.bdens.main()
        return counts

    def _get_topodist_from_graph(self):
        """Create an array of the topological distance of each
        point on the graph.
        """
        dists_ax = np.zeros(self.graph.number_of_nodes())
        dists_dend = dists_ax.copy()
        for idx, node in enumerate(self.graph.nodes()):
            if "Axon" in node.tree_type:
                dists_ax[idx] = node.dist_to_body
            elif "Dend" in node.tree_type:
                dists_dend[idx] = node.dist_to_body

        return dists_ax, dists_dend

    def _get_nonzero_points_on_tree(self, tree: np.ndarray) -> np.ndarray:
        """Returns all of the non-zero points on a given tree,
        which is the axonal or dendritic tree of the neuron. Filtering
        these zero points out is required when you wish to plot the
        axonal and dendritic distribution of the hiddenness, for example.
        """
        return tree.nonzero()

    def _plot_ur_topo(self, ax: plt.Axes, topodist: np.ndarray, nonzero: np.ndarray, points_type: NeuronType):
        """Genereates a plot of the Branching Density U(r)
        as a function of the topological distance of the node.
        Receives in advance the indices that mark the location of the
        axonal and dendritic points on the trees containing the data.
        """
        ax.scatter(
            topodist[nonzero],
            self.ur[self.r].iloc[nonzero],
            s=0.2,
            c=self.color[points_type],
            alpha=0.3,
        )
        ax.set_xlabel("Topological distance [um]")
        ax.set_ylabel(f"U(r={self.r})")
        ax.set_title(
            f"U(r) as a function of the topological distance of the node, {self.bdens.neuron_fname.stem}"
        )

    def _conform_ur_to_new_idx(self, topodist: np.ndarray, ur: pd.Series, window=10):
        """Creates a new index to U(r) based on the topological distance of each point with a higher, fixed resolution.
        This operation preserves the current known information about the distance of each
        point from the origin, but adds a bunch of new ones to make the grid
        between 0 and the max existing topological distance uniform. This should allow us
        to compute a better running average since the data is sampled uniformly.
        """
        topodist = self._remove_topodist_dups(topodist)
        uniform_topodist = np.arange(topodist.max(), step=0.25)
        dist = scipy.spatial.distance.cdist(
            np.atleast_2d(topodist).T, np.atleast_2d(uniform_topodist).T
        ).argmin(axis=1)
        # The var dist contains the closest value in uniform_topodist to the old
        # values in topodist. We'll now replace the values in the new index with
        # the values of the old one, so that we do not change the given raw data.
        uniform_topodist[dist] = topodist
        ur_with_distance_as_idx = (
            pd.DataFrame(ur.reset_index(drop=True))
            .assign(topodist=topodist)
            .set_index("topodist")
            .reindex(uniform_topodist)
        )
        full_ur = ur_with_distance_as_idx.interpolate('cubic')
        mean = full_ur.rolling(window=window).mean().dropna()
        return mean

    def _remove_topodist_dups(self, topodist: np.ndarray) -> np.ndarray:
        """Finds duplicate values in the given floating-point array and
        changes them by a small fraction to make all values unique."""
        counts = pd.Series(topodist).value_counts()
        counts = counts[counts >= 2].reset_index()["index"]
        delta = np.arange(0.01, 0., -0.001)
        for dupval in counts:
            dup_indices = np.where(topodist == dupval)[0]
            for idx, cur_delta in zip(dup_indices, delta):
                topodist[idx] -= cur_delta
        return topodist

    @staticmethod
    def _fft_ur(data: Union[np.ndarray, pd.Series], sample_freq: float):
        """Calculates the FFT of the given data.
        sample_freq is the number of samples per second. """
        n = data.shape[0]
        half_of_n = np.int(n / 2)
        f = 1 / sample_freq
        x = np.linspace(0.0, 1.0 / (2.0 * f), half_of_n)
        fft = scipy.fftpack.fft(data)
        positive_freqs = 2 / n * np.abs(fft[:half_of_n])
        return x, positive_freqs

    def _plot_fft(self, x, y, ax: plt.Axes, neuron_type: NeuronType):
        ax.plot(x, y, c=self.color[neuron_type])
        ax.set_xlabel("Frequency [1/um]")
        ax.set_ylabel("Power")
        ax.set_title(f"FFT analysis of the density of neuron {self.bdens.neuron_fname.stem}")


@attr.s
class DensityCollisionsDistance:
    """A class designed to show a 3D scatter plot, in which each
    point on the neural tree is assigned three values - its
    distance from the soma, the number of collisions and the density U(r) of
    it.
    """

    bdens = attr.ib(validator=instance_of(BranchDensity))
    graph = attr.ib(validator=instance_of(nx.Graph))
    r = attr.ib(default=10, validator=instance_of(int))
    ur = attr.ib(init=False)
    topodist_ax = attr.ib(init=False)
    topodist_dend = attr.ib(init=False)
    eucdist_ax = attr.ib(init=False)
    eucdist_dend = attr.ib(init=False)

    def main(self):
        """ Main pipeline """
        self.ur = self._get_density_from_bdens()
        self.topodist_ax, self.topodist_dend = self._get_topodist_from_graph()
        self._populate_ur_with_colls()
        self._scatter()

    def _get_density_from_bdens(self):
        """Runs the main analysis pipeline of the BranchDensity class to
        receive a DataFrame containing the density data per radius.
        :return pd.DataFrame:
        """
        density = self.bdens.main()
        return density

    def _get_topodist_from_graph(self):
        """Create an array of the topological distance of each
        point on the graph.
        """
        dists_ax = np.zeros(self.graph.number_of_nodes())
        dists_dend = dists_ax.copy()
        for idx, node in enumerate(self.graph.nodes()):
            if "Axon" in node.tree_type:
                dists_ax[idx] = node.dist_to_body
            elif "Dend" in node.tree_type:
                dists_dend[idx] = node.dist_to_body

        return dists_ax, dists_dend

    def _populate_ur_with_colls(self):
        self.ur["collisions"] = 0
        for row_idx, node in enumerate(self.graph.nodes()):
            self.ur.iloc[row_idx, -1] = node.collisions

    def _scatter(self):
        """Genereates a 3D scatter plot of the density, collision count and
        distance of each neural point.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        nonzero_ax = self.topodist_ax.nonzero()
        nonzero_dend = self.topodist_dend.nonzero()
        ax.scatter(
            self.topodist_ax[nonzero_ax],
            self.ur[self.r].iloc[nonzero_ax],
            self.ur.loc[nonzero_ax, "collisions"],
            s=0.25,
            c="C2",
            alpha=0.5,
        )
        ax.scatter(
            self.topodist_dend[nonzero_dend],
            self.ur[self.r].iloc[nonzero_dend],
            self.ur.loc[nonzero_dend, "collisions"],
            s=0.25,
            c="C1",
            alpha=0.5,
        )
        ax.set_xlabel("Topological distance [um]")
        ax.set_ylabel(f"U(r={self.r})")
        ax.set_zlabel(f"# Collisions")
        ax.set_title(
            f"# Collisions, U(r) as a function of topological distance, {self.bdens.neuron_fname.stem}"
        )
        ax.legend(["Axon", "Dendrite"])
        fig.savefig(
            f"results/2019_2_10/density_topodist_collisions_r_{self.r}_{self.bdens.neuron_fname.stem}.pdf",
            transparent=True,
        )


def run_ur_topodist_colls():
    """Plots the number of collisions and U(r) as a function
    of the topological distance of each point on the neural tree.
    """
    for neuron_name in neuron_names:
        bdens_coll_topodist = _instantiate_bdens(
            neuron_name, branch_class=DensityCollisionsDistance
        )
        if bdens_coll_topodist:
            bdens_coll_topodist.main()
    plt.show()


def run_ur_topodist():
    """Plots the branching density U(r) of every point on the
    neural tree as a function of the topological distance of
    that same point.
    """
    for neuron_name in neuron_names:
        bdens_coll = _instantiate_bdens(neuron_name, branch_class=BranchDensityAndDist)
        if bdens_coll:
            bdens_coll.main()
    plt.show()


def run_ur_topodist_multiple_r():
    """Plots the branching density U(r) of every point on the
    neural tree as a function of the topological distance of
    that same point. Does so for a single neuron over multiple
    r's.
    """
    neuron_name = "AP120410_s3c1"
    radii = range(1, 11)
    for radius in radii:
        bdens_coll = _instantiate_bdens(
            neuron_name, branch_class=BranchDensityAndDist, r=radius
        )
        if bdens_coll:
            bdens_coll.main()
    plt.show()


def run_single_neuron_with_jointplot():
    """
    Creates a single collisions-to-density jointplot, i.e. a scatter
    plot with the histograms of the two axes on its sides.
    """
    neuron_names = [
        "AP120410_s3c1",
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
        # "AP131105_s1c1",
    ]
    for neuron_name in neuron_names:
        bdens_coll = _instantiate_bdens(neuron_name)
        bdens_coll.main(plot=False)
        bdens_coll.plot_colls_dens_jointplot(neuron_name)
    plt.show()


def run_collisions_dens_jointplot_multiple_r():
    """Creates a single collisions-to-density jointplot, i.e. a scatter
    plot with the histograms of the two axes on its sides. It does
    so for a single neuron with multiple U(r) radii.
    """
    neuron_name = "AP120410_s3c1"
    radii = range(1, 11)
    for radius in radii:
        bdens_coll = _instantiate_bdens(
            neuron_name, branch_class=BranchDensityAndCollisions, r=radius
        )
        bdens_coll.main(plot=False)
        bdens_coll.plot_colls_dens_jointplot(neuron_name)
    plt.show()


def _instantiate_bdens(neuron_name, branch_class=BranchDensityAndCollisions, r=10):
    """
    Helper method to instantiate a BranchDensity instance,
    as well as either a BranchDensityAndCollisions instance, a
    BranchDensityAndDist instance or a DensityDistCollisions
    instance. branch_class can be either one of these classes.
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
    bdens_coll = branch_class(bdens, graph, r=r)
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
        "AP131105_s1c1"
    ]
    perc = 90
    for neuron_name in neuron_names:
        bdens_coll = _instantiate_bdens(neuron_name)
        if not bdens_coll:
            continue
        colls = bdens_coll.get_top_colls_percentile(perc)
        fname = (
            pathlib.Path(__file__).resolve().parents[3]
            / "results"
            / "2019_2_10"
            / f"top_{100-perc}p_likely_colls_{neuron_name}.npy"
        )
        np.save(fname, colls)


if __name__ == "__main__":
    # run_multiple_neurons()
    # run_single_neuron_with_jointplot()
    # run_single_neuron_with_quantile()
    run_ur_topodist()
    # run_ur_topodist_multiple_r()
    # run_collisions_dens_jointplot_multiple_r()
    # run_ur_topodist_colls()

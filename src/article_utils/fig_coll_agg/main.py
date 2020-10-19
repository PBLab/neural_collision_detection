import pathlib
import multiprocessing

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from ncd_post_process.create_neuron_id import collisions_vs_dist_naive

neuron_names = ["AP120412_s3c2", "AP130312_s1c1"]
results_folder = pathlib.Path("results/2020_09_05")
data_folder = pathlib.Path("results/for_article/fig_coll_agg")


def pipe_single_neuron(neuron, results_folder):
    coll_dist = collisions_vs_dist_naive._neuron_to_obj(neuron, results_folder)
    coll_dist.run()
    coll_dist.parsed_axon["neuron"] = neuron
    coll_dist.parsed_axon["neurite"] = "axon"
    coll_dist.parsed_dend["neuron"] = neuron
    coll_dist.parsed_dend["neurite"] = "dendrite"
    return coll_dist


def plot_combined_joint(data, name):
    data = pd.concat(data, ignore_index=True)
    data = data.rename(
        {"dist": "Length of branch [um]", "coll": f"{name} chance for collision"},
        axis=1,
    )
    sns.jointplot(
        data=data,
        x="Length of branch [um]",
        y=f"{name} chance for collision",
        kind="hist",
        hue="neuron",
        height=8,
        joint_kws={"bins": 20},
    )


def plot_single_neuron(data, name: str) -> sns.JointGrid:
    """Generates a distance-collisions jointplot of a single neuron.

    For the given object with the neuron name, the function will generate a
    jointplot with the normalized collision chance in the y axis and the
    topological distance on the x. The center of the jointplot is a hexbin
    plot and the sides are the distributions of the variables.

    Parameters
    ----------
    data : CollisionsDistNaive
    name : str
        The neuron's name

    Returns
    -------
    sns.JointGrid
    """

    single_neuron = pd.concat([data.parsed_dend, data.parsed_axon], ignore_index=True)
    single_neuron = single_neuron.rename(
        {
            "dist": "Length of branch [um]",
            "coll": "Chance for collision",
            "coll_normed": "Normalized chance for collision",
        },
        axis=1,
    )
    g = sns.JointGrid(height=8)
    x_ax = single_neuron.query('neurite == "axon"')["Length of branch [um]"]
    y_ax = single_neuron.query('neurite == "axon"')["Normalized chance for collision"]
    extent_ax = (x_ax.min(), x_ax.max(), 0, y_ax.max())
    x_dend = single_neuron.query('neurite == "dendrite"')["Length of branch [um]"]
    y_dend = single_neuron.query('neurite == "dendrite"')[
        "Normalized chance for collision"
    ]
    g.ax_joint.hexbin(
        x=x_ax,
        y=y_ax,
        gridsize=30,
        alpha=0.7,
        edgecolors=None,
        cmap="Greens",
        mincnt=1,
        extent=extent_ax,
    )
    g.ax_joint.hexbin(
        x=x_dend,
        y=y_dend,
        gridsize=30,
        alpha=0.7,
        edgecolors=None,
        cmap="Oranges",
        mincnt=1,
        extent=extent_ax,
    )
    sns.histplot(x=x_ax, alpha=0.5, ax=g.ax_marg_x, color="C2")
    sns.histplot(x=x_dend, alpha=0.5, ax=g.ax_marg_x, color="C1")
    sns.histplot(y=y_ax, alpha=0.5, ax=g.ax_marg_y, color="C2", bins=20)
    sns.histplot(y=y_dend, alpha=0.5, ax=g.ax_marg_y, color="C1", bins=5)
    g.ax_joint.set_xlabel("Length of branch [um]")
    g.ax_joint.set_ylabel("Normalized chance for collision")
    plt.tight_layout()
    sns.despine(trim=True, ax=g.ax_joint)
    g.ax_joint.figure.savefig(
        "results/for_article/fig_coll_agg/coll_vs_dist_single_neuron.pdf",
        transparent=True,
        dpi=300,
    )
    plt.show(block=False)

    return g


if __name__ == "__main__":
    with multiprocessing.Pool() as pool:
        coll_dist_objects = pool.starmap(
            pipe_single_neuron, ((name, results_folder) for name in neuron_names)
        )
    axons = (coll_dist.parsed_axon for coll_dist in coll_dist_objects)
    dends = (coll_dist.parsed_dend for coll_dist in coll_dist_objects)
    gridplot = plot_single_neuron(coll_dist_objects[0], neuron_names[0])
    # for neurite, name in zip([axons, dends], ["axon", "dendrite"]):
    #     plot_combined_joint(neurite, name)

    plt.show()

"""This script plots the correlation between the alpha values and the
U(r=10) metric which we used at the start of this project to check
density of the neuron with.
"""
import pathlib

import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.alpha_shapes.distance_alpha import generate_df_from_neuron
from ncd_post_process.lib import find_branching_density

neuron_names = [
    "AP120507_s3c1",
    "AP131105_s1c1",
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
    "AP120522_s3c1",
    "AP120523_s2c1",
    "AP130110_s2c1",
    "AP130606_s2c1",
    "AP120507_s3c1",
    "MW120607_LH3",
]


def plot_alpha_vs_density(points, name):
    """Shows a scatterplot of the alpha value vs. the
    neuronal density."""
    ax = sns.scatterplot(data=points.reset_index(), x='alpha', y='U(r=10)', hue='type', alpha=0.3)
    ax.set_xscale('log')
    plt.show(block=False)
    ax.figure.savefig(f'results/with_alpha/alpha_vs_u(r)_{name}.pdf', transparent=True, dpi=300)


def main(neuron_fname: pathlib.Path, neuron_name: str, py3dn_folder: pathlib.Path, graph_fname: pathlib.Path):
    try:
        points, g = generate_df_from_neuron(graph_fname, neuron_name)
    except FileNotFoundError:
        raise
    bdens = find_branching_density.BranchDensity(neuron_fname, py3dn_folder)
    counts = bdens.main()
    points.loc[:, "U(r=10)"] = counts.loc[:, 10].to_numpy()
    return points, g


if __name__ == '__main__':
    py3dn_folder = pathlib.Path('/data/neural_collision_detection') / "py3DN"
    for neuron_name in neuron_names:
        neuron_fname = (
            pathlib.Path('/data/neural_collision_detection')
            / "data"
            / "neurons"
            / f"{neuron_name}.xml"
        )
        graph_fname = pathlib.Path(f'/data/neural_collision_detection/results/2020_07_29/graph_{neuron_name}_with_collisions.gml')
        try:
            points, g = main(neuron_fname, neuron_name, py3dn_folder, graph_fname)
        except FileNotFoundError:
            continue
        plot_alpha_vs_density(points, neuron_name)

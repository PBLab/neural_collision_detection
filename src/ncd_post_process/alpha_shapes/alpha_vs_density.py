"""This script plots the correlation between the alpha values and the
U(r=10) metric which we used at the start of this project to check
density of the neuron with.
"""
import pathlib

import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.alpha_shapes.distance_alpha import generate_df_from_neuron
from ncd_post_process.create_neuron_id import find_branching_density

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


def plot_alpha_vs_density(points, name):
    ax = sns.scatterplot(data=points.reset_index(), x='alpha', y='U(r=10)', hue='type', alpha=0.3)
    ax.set_xscale('log')
    plt.show()
    ax.figure.savefig(f'results/for_article/fig2/alpha_vs_u(r)_{name}.pdf', transparent=True, dpi=300)


def main(neuron_fname: pathlib.Path, neuron_name: str, py3dn_folder: pathlib.Path, graph_fname: pathlib.Path):
    points, g = generate_df_from_neuron(graph_fname, neuron_name)
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
        graph_fname = pathlib.Path(f'/data/neural_collision_detection/results/2020_02_14/graph_{neuron_name}_with_collisions.gml')
        points, g = main(neuron_fname, neuron_name, py3dn_folder, graph_fname)
        plot_alpha_vs_density(points, neuron_name)

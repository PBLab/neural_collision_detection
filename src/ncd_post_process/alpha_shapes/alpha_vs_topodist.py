import pathlib

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

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


def plot_alpha_vs_dist(points, name):
    ax = sns.scatterplot(data=points.reset_index(), x='dist', y='alpha', hue='type', alpha=0.3)
    ax.set_yscale('log')
    plt.show()
    ax.figure.savefig(f'results/for_article/fig2/alpha_vs_dist_{name}.pdf', transparent=True, dpi=300)


def main(graph_fname: pathlib.Path, neuron_name: str):
    points, g = generate_df_from_neuron(graph_fname, neuron_name)
    return points, g



if __name__ == '__main__':
    for neuron_name in neuron_names:
        graph_fname = pathlib.Path(f'results/2020_02_14/graph_{neuron_name}_with_collisions.gml')
        points, g = main(graph_fname, neuron_name)
        plot_alpha_vs_dist(points, neuron_name)
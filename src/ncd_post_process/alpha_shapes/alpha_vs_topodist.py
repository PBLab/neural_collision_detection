import pathlib

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.alpha_shapes.distance_alpha import generate_df_from_neuron
from article_utils.fig_alpha_agg.plot_axondend_distrib import MAX_ALLOWED_ALPHA


neuron_names = [
    # "AP120507_s3c1",
    # "AP131105_s1c1",
    # "AP120410_s1c1",
    # "AP120410_s3c1",
    "AP120412_s3c2",
    # "AP120416_s3c1",
    # "AP120419_s1c1",
    # "AP120420_s1c1",
    # "AP120420_s2c1",
    # "AP120510_s1c1",
    # "AP120524_s2c1",
    # "AP120614_s1c2",
    # "AP130312_s1c1",
    # "AP120522_s3c1",
    # "AP120523_s2c1",
    # "AP130110_s2c1",
    # "AP130606_s2c1",
    # "AP120507_s3c1",
    # "MW120607_LH3",
]


def plot_alpha_vs_dist(points, name):
    data = points.reset_index()
    data.loc[:, 'alpha'] = np.log(data.loc[:, 'alpha'] + 1)
    palette = ['C2', 'C1', 'C0', 'C3', 'C4', 'C5', 'C6']
    num_colors = len(data.loc[:, 'type'].unique())
    ax = sns.scatterplot(data=data, x='alpha', y='dist', hue='type', alpha=0.3, palette=palette[:num_colors], legend=False)
    ax.axvline(np.log(MAX_ALLOWED_ALPHA + 1), 0, 500, color='red')
    sns.despine(ax=ax, trim=True)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.figure.savefig(f'results/for_article/fig_alpha_agg/alpha_vs_dist_{name}.pdf', transparent=True, dpi=300)
    ax.figure.savefig(f'results/for_article/fig_alpha_agg/alpha_vs_dist_{name}.png', transparent=True, dpi=300)


def main(graph_fname: pathlib.Path, neuron_name: str):
    try:
        points, g = generate_df_from_neuron(graph_fname, neuron_name)
    except FileNotFoundError:
        raise
    return points, g


if __name__ == '__main__':
    for neuron_name in neuron_names:
        graph_fname = pathlib.Path(f'results/2020_09_05/graph_{neuron_name}_with_collisions.gml')
        try:
            points, g = main(graph_fname, neuron_name)
        except FileNotFoundError:
            continue
        plot_alpha_vs_dist(points, neuron_name)
    plt.show(block=False)

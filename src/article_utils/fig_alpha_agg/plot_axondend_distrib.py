import pathlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from article_utils.fig_alpha_3dviz import display_cgal_alphas_napari

MAX_ALLOWED_ALPHA = 3163

neuron_names = [
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
    "AP130312_s1c1",
]

metadata = (('green', 'ax'), ('orange', 'dend'))


def ax_dend_alpha_distrib(ax: pd.DataFrame, dend: pd.DataFrame, name: str):
    axon_data = np.log(ax.loc[:, 'alpha'] + 1)
    dend_data = np.log(dend.loc[:, 'alpha'] + 1)
    fig, ax_hist = plt.subplots()
    for (data, meta) in zip([axon_data, dend_data], metadata):
        ax_hist.hist(data, bins=100, color=meta[0], label=meta[1], alpha=0.5)

    ax_hist.legend()
    ax_hist.axvline(np.log(MAX_ALLOWED_ALPHA + 1), 0,  1000, color='red')
    ax_hist.set_title(name)
    sns.despine(ax=ax_hist, trim=True)
    fig.savefig(f'results/for_article/fig_alpha_agg/{name}_alpha_value_distribution.pdf', transparent=True, dpi=300)


if __name__ == '__main__':
    for name in neuron_names:
        points, graph = display_cgal_alphas_napari.load_complete_neuronal_data(name, pathlib.Path('results/2020_09_05'))
        inside_vasc_points = points.query('alpha <= @MAX_ALLOWED_ALPHA')
        ax_all, dend_all = display_cgal_alphas_napari.separate_ax_dend(points)
        ax_dend_alpha_distrib(ax_all, dend_all, name)
        ax_filt, dend_filt = display_cgal_alphas_napari.separate_ax_dend(inside_vasc_points)
        ax_dend_alpha_distrib(ax_filt, dend_filt, name + "_FILT")
    plt.show(block=False)

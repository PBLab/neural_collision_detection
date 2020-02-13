import pathlib

import numpy as np
import napari
import vispy.color
import matplotlib.pyplot as plt

from find_collisions_distribution import load_collisions, histogram_colls_3d
from ncd_post_process.render_with_napari import create_napari_surface


def make_and_save_colorbar(img, min_, max_):
    """Helper func to save a colorbar containing
    the probability of collision.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(img, cmap='gist_yarg')
    ax.axis('off')
    plt.rcParams.update({'font.size': 26})
    fig.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.gist_yarg, norm=plt.Normalize(vmin=min_, vmax=max_)))
    plt.show()
    fig.savefig("/data/neural_collision_detection/results/for_article/fig1/colls_with_colorbar.png", transparent=True, dpi=300)


def run(obj: pathlib.Path, colls: pathlib.Path):
    colls = load_collisions(colls)
    colls_hist = histogram_colls_3d(colls)
    colls_hist /= colls_hist.sum()
    surface = create_napari_surface(obj)
    colormap = vispy.color.Colormap(plt.cm.gist_yarg(np.linspace(0, 1, 256)))
    with napari.gui_qt():
        v = napari.view_image(colls_hist, ndisplay=3, rgb=False, colormap=colormap)
        v.theme = 'light'
        v.add_surface(surface, colormap='magenta')
        img = v.screenshot()
        # imageio.imwrite('/data/neural_collision_detection/results/for_article/fig1/toy_neuron_only_collisions.png', img[:, :,:3], transparency=(255, 255, 255), dpi=(300, 300), prefer_uint8=False)
    make_and_save_colorbar(img, colls_hist.min(), colls_hist.max())


if __name__ == "__main__":
    neuron_obj_fname = "/data/neural_collision_detection/results/for_article/fig1/artificial_neuron.obj"
    neuron_colls_fname = "/data/neural_collision_detection/results/for_article/fig1/normalized_artificial_neuron_results_agg_thresh_0.npz"

    run(neuron_obj_fname, neuron_colls_fname)

import pathlib

import numpy as np
import napari
import vispy.color
import matplotlib.pyplot as plt

from article_utils.fig1.find_collisions_distribution import load_collisions, histogram_colls_3d
from ncd_post_process.render_with_napari import create_napari_surface


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
        # imageio.imsave('/data/neural_collision_detection/results/for_article/supp_colls/toy_neuron_with_collisions.png', img)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(img, cmap='gist_yarg')
    ax.axis('off')
    fig.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.gist_yarg, norm=plt.Normalize(vmin=colls_hist.min(), vmax=colls_hist.max())))
    plt.show()
    fig.savefig("/data/neural_collision_detection/results/for_article/supp_colls/supp_colls.png", transparent=True, dpi=300)


if __name__ == "__main__":
    neuron_obj_fname = "/data/neural_collision_detection/results/for_article/supp_colls/artificial_neuron.obj"
    neuron_colls_fname = "/data/neural_collision_detection/results/for_article/supp_colls/normalized_artificial_neuron_results_agg_thresh_0.npz"

    run(neuron_obj_fname, neuron_colls_fname)

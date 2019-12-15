"""
The goal of this script is to find the chance of collision for each of the points on
the simulated neuron. This is done by computing the distance of the collisions to the
nearest neural point, and summing it up.
"""
import scipy.spatial
import pandas as pd
import numpy as np
import napari
import vispy.color


def load_neuron(fname):
    return pd.read_csv(fname, header=None, names=['x', 'y', 'z', 'r']).to_numpy()[:, :3]


def load_collisions(fname):
    colls = np.load(fname)["neuron_coords"]
    allnan_rows = np.where(np.all(np.isnan(colls), axis=1))[0]
    return np.delete(colls, allnan_rows, axis=0)


def calculate_distances(colls, neuron):
    dist = scipy.spatial.distance.cdist(colls, neuron)
    colls_on_neuron = dist.argmin(axis=1).astype(np.int32)
    return np.bincount(colls_on_neuron, minlength=len(neuron))


if __name__ == '__main__':
    colls = load_collisions('/data/neural_collision_detection/results/for_article/fig1/normalized_artificial_neuron_results_agg_thresh_0.npz')
    neuron = load_neuron('/data/neural_collision_detection/results/for_article/fig1/artificial_neuron.csv')
    distcount = calculate_distances(colls, neuron)
    distcount = (distcount / distcount.max()) * 10
    cmap = vispy.color.get_colormap("viridis")
    colors = cmap[distcount].rgba
    with napari.gui_qt():
        v = napari.view_points(neuron, n_dimensional=True, size=1.2, edge_width=0., face_color=colors)
        v.theme = 'light'
        # img = v.screenshot()
        # imageio.imsave('/data/neural_collision_detection/results/for_article/fig1/toy_neuron_with_collisions.png', img)

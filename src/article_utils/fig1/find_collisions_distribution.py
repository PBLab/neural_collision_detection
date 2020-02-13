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
import matplotlib.pyplot as plt


def load_neuron(fname):
    return pd.read_csv(fname, header=None, names=['x', 'y', 'z', 'r']).to_numpy()[:, :3]


def load_collisions(fname):
    colls = np.load(fname)["neuron_coords"]
    allnan_rows = np.where(np.all(np.isnan(colls), axis=1))[0]
    return np.delete(colls, allnan_rows, axis=0)


def normalize_counts(data):
    """Allow showing the underlying distribution of the data
    by first normalizing it.
    Data is a 3-column array of coordinates.
    """
    data = data.sum(axis=1)
    data -= data.min()
    data.sort()
    return data


def histogram_colls_3d(colls, nominal_bins=40):
    """Histograms the collision counts into a 3D hist
    with about ``nominal_bins`` number of bins in each
    axis.

    Returns a napari-viewable 3D array.
    """
    mins = colls.min(axis=0)
    maxs = colls.max(axis=0)
    bins_per_ax = (nominal_bins * colls.ptp(axis=0) / 100).astype(int)
    x_edges = np.linspace(mins[0], maxs[0], num=bins_per_ax[0])
    y_edges = np.linspace(mins[1], maxs[1], num=bins_per_ax[1])
    z_edges = np.linspace(mins[2], maxs[2], num=bins_per_ax[2])
    return np.histogramdd(colls, [x_edges, y_edges, z_edges])[0]


if __name__ == '__main__':
    colls = load_collisions('/data/neural_collision_detection/results/for_article/fig1/normalized_artificial_neuron_results_agg_thresh_0.npz')
    colls_normed = normalize_counts(colls)
    neuron = load_neuron('/data/neural_collision_detection/results/for_article/fig1/artificial_neuron_balls.csv')
    neuron_normed = normalize_counts(neuron)
    colls_hist = histogram_colls_3d(colls)
    colormap = 'Greys_r', vispy.color.Colormap(plt.cm.Greys_r(np.linspace(0, 1, 256)))
    with napari.gui_qt():
        # neuron -= neuron.min(axis=0)
        # v = napari.view_points(neuron, size=1.2, edge_width=0, face_color='magenta', name='neuron')
        v = napari.view_image(colls_hist, ndisplay=3, rgb=False, colormap=vispy.color.Colormap(plt.cm.Greys_r(np.linspace(0, 1, 256))))
        # v.add_points(colls[::10], size=1.2, edge_width=0, face_color='black', symbol='x', name='colls')
        v.theme = 'light'
        # img = v.screenshot()
        # imageio.imsave('/data/neural_collision_detection/results/for_article/fig1/toy_neuron_with_collisions.png', img)

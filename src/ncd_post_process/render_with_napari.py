"""Unneeded currently"""
import pathlib

from dask.distributed import Client
import dask
import napari
import numpy as np
import pandas as pd
from vispy.color import ColorArray
from collections import namedtuple
from skimage import exposure

from ncd_post_process.graph_parsing import (
    connect_collisions_to_neural_points,
    NeuronToGraph,
)


HistEdges = namedtuple("HistEdges", ["hist", "edges"])
HistMetadata = namedtuple("HistMetadata", ["hist", "starts", "ends"])
PointsColor = namedtuple("PointColor", ["points", "color"])


# @dask.delayed
def create_napari_surface(obj_fname):
    """Loads the given fname, which is assumed to be an .obj file,
    and returns it as a napari-configured Surface that can be easily rendered.
    """
    obj = pd.read_csv(
        obj_fname, sep=" ", header=None, index_col=0, names=["h", "x", "y", "z"]
    )
    # obj = obj.reindex(columns=['h', 'y', 'x', 'z'])
    # obj.columns = ['h', 'x', 'y', 'z']
    vertices = obj.loc["v", :].to_numpy()
    xx = vertices[:, 0].copy()
    vertices[:, 0] = vertices[:, 1]
    vertices[:, 1] = xx
    faces = obj.loc["f", :].to_numpy().astype(np.uint64) - 1
    values = np.ones((len(vertices),))
    return (vertices, faces, values, len(vertices))


# @dask.delayed
def load_collisions(colls_fname, downsample_factor=1, key="neuron_coords"):
    """Loads collisions with the input array being an Nx3 array, each row
    being a coordinate on top of the neuron that collided with the
    vasculature.
    """
    fname = pathlib.Path(colls_fname)
    assert fname.exists()
    collisions = np.load(fname)[key][::downsample_factor, :]
    return collisions


# @dask.delayed
def filter_nans(collisions):
    """Remove all-nan collisions from the array."""
    allnan_rows = np.where(np.all(np.isnan(collisions), axis=1))[0]
    collisions = np.delete(collisions, allnan_rows, axis=0)
    return collisions


# @dask.delayed
def gen_hist(collisions, binsize: tuple):
    """ Histograms the collisions into l-sized bins """
    max_x, min_x = np.max(collisions[:, 0]), np.min(collisions[:, 0])
    max_y, min_y = np.max(collisions[:, 1]), np.min(collisions[:, 1])
    max_z, min_z = np.max(collisions[:, 2]), np.min(collisions[:, 2])
    bins_x = int(np.ceil((max_x - min_x) / binsize[0]))
    bins_y = int(np.ceil((max_y - min_y) / binsize[1]))
    bins_z = int(np.ceil((max_z - min_z) / binsize[2]))
    hist, edges = np.histogramdd(collisions, bins=(bins_x, bins_y, bins_z))

    return HistEdges(hist, edges)


# @dask.delayed
def filter_relevant_bins(hist_edges):
    """After generating the histogram of collisions, filters out only
    the bins in which a collisions occurred. It then generates two
    arrays which contain the start and end of the bins containing the
    collisions in microns.
    """
    hist, edges = hist_edges
    relevant_coords = np.where(
        hist > 0
    )  # each row is a dimension, each column a coordinate
    num_dims = 3
    num_ones = len(relevant_coords[0])
    bin_starts = np.zeros((num_ones, num_dims))
    bin_ends = np.zeros_like(bin_starts)
    assert len(edges) == len(relevant_coords)
    for coor_idx, (coor, edge) in enumerate(zip(relevant_coords, edges)):
        bin_starts[:, coor_idx] = edge[coor]
        bin_ends[:, coor_idx] = edge[coor + 1]

    return HistMetadata(hist[relevant_coords], bin_starts, bin_ends)


# @dask.delayed
def hist_into_points(hist_metadata):
    """Iterate over all bins and create an array
    with points, value of which is the value of the histogram at that
    point."""
    hist, starts, ends = hist_metadata
    points_arr = np.zeros((len(starts), 3))
    color_arr = []
    norm = 1.0 / (hist.max())
    loc = np.array([0.0, 0.0, 0.0])
    for idx, (val, coll_start, coll_end) in enumerate(zip(hist, starts, ends)):
        loc[:] = (coll_start + coll_end) / 2
        points_arr[idx] = loc
        color_arr.append((val * norm, 0.0, 0.0, 1.0))
    return PointsColor(points_arr, ColorArray(color_arr))


# @dask.delayed
def add_colls_data_to_surface(surface, neural_collisions):
    normed = (neural_collisions - neural_collisions.min()) + 0.5
    normed = normed / normed.max()
    return (surface[0].to_numpy(), surface[1], normed)


if __name__ == "__main__":
    client = Client(processes=False)
    neuron_name = "AP130312_s1c1"
    neuron_obj_fname = f"/data/neural_collision_detection/src/convert_obj_matlab/{neuron_name}_yz_flipped.obj"
    # neuron_obj_fname = '/data/neural_collision_detection/yoav/artificial_270120/neuron.obj'
    surface = client.submit(create_napari_surface, neuron_obj_fname)
    # colls_fname = "/data/neural_collision_detection/results/for_article/fig1/normalized_artificial_neuron_results_agg_thresh_0.npz"
    # collisions = client.submit(load_collisions, colls_fname, 1, "neuron_coords")
    # collisions = client.submit(filter_nans, collisions)
    surface = surface.result()
    # closest_idx = client.submit(connect_collisions_to_neural_points, collisions, surface[0])
    # neural_collisions = client.submit(NeuronToGraph.coerce_collisions_to_neural_coords, surface[3], closest_idx)
    # binsize = (1, 1, 1)
    # hist_and_edges = gen_hist(collisions, binsize)
    # hist_and_metadata = filter_relevant_bins(hist_and_edges)
    # points_and_color = hist_into_points(hist_and_metadata)
    # surface_with_collisions = client.submit(add_colls_data_to_surface, surface, neural_collisions)
    # surface_with_collisions = surface_with_collisions.result()
    # colors = np.zeros((len(surface_with_collisions[0]), 4))
    # colors[:, 0] = 1.0
    # colors[:, 3] = surface_with_collisions[2]
    # colors = ColorArray(colors)
    # colors = [color.rgba.ravel() for color in colors]
    raw_neuron = pd.read_csv(
        f"/data/neural_collision_detection/src/convert_obj_matlab/{neuron_name}_balls_yz_flipped.csv",
        header=None,
        names=["x", "y", "z", "r"],
    )
    with napari.gui_qt():
        # viewer = napari.view_points(collisions.result()[::10], size=1, face_color='pink')
        viewer = napari.view_points(
            raw_neuron.iloc[:, :3].to_numpy(), size=1, face_color="white"
        )
        viewer.add_surface(surface, colormap="magenta")

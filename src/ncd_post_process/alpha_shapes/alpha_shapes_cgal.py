import pathlib
import sys
from itertools import chain
import multiprocessing

import numpy as np
import pandas as pd
import dask

sys.path.append('/data/MatlabCode/PBLabToolkit/External/cgal-python-bindings/src/alpha3_bindings/delaunay_fast_location_release')
from tri3_epic import *
sys.path.pop(-1)

dask.config.set(scheduler='processes')


def generate_alphashape_from_neuron(neuron_name):
    """For a given neuron name, iterate over its points and return
    an Alpha Shape object.
    """
    all_points = []
    points = pd.read_csv(neuron_name, header=None)
    for _, point in points.iterrows():
        all_points.append(Point_3(point.iloc[0], point.iloc[1], point.iloc[2]))
    return Alpha_shape_3(all_points), all_points


def get_all_alpha_values(shp: Alpha_shape_3):
    """Returns an array of all needed alpha shapes"""
    num = range(shp.number_of_alphas())
    alphas = [shp.get_nth_alpha(idx) for idx in num]
    alphas.pop(0)  # always 0
    return alphas


@dask.delayed
def classify_points(shp: Alpha_shape_3, points: list) -> dict:
    """Iterates over the points of the alpha shape and classifies them,
    returning a dict with their values."""
    keys = Classification_type.names.values()
    classified = {key: [] for key in keys}
    for point in points:
        classified[shp.classify(point)].append([np.float32(point.x()), np.float32(point.y()), np.float32(point.z())])
    return {key: np.asarray(val, dtype=np.float32) for key, val in classified.items()}


@dask.delayed
def _dict_to_series(to_ser, alpha):
    """Convert a dict (of classify_points) to a DataFrame.

    The index of the DF will be the (x, y, z) points, while the
    values are the labels ('classification') given to each of them."""
    index = []
    data = []
    for key, val in to_ser.items():
        if len(val) == 0:
            continue
        data.append([str(key)] * len(val))
        index.append(val)
    df = pd.DataFrame(chain.from_iterable(data), columns=[alpha])
    df.index.names = ['num']
    index = pd.MultiIndex.from_frame(pd.DataFrame(list(chain.from_iterable(index)), columns=['x', 'y', 'z']))
    df = df.set_index(index, append=True)
    return df


def process_single_alpha(alpha, alpha_shape, points):
    alpha_shape.set_alpha(alpha)
    classified = classify_points(alpha_shape, points)
    classified_df = _dict_to_series(classified, alpha)
    return classified_df


def sample_alphas(alphas, factor=10):
    len_ = len(alphas)
    alphas = np.asarray(alphas)
    return alphas[np.linspace(0, len_-1, len_ // factor, dtype=np.uint32)]


if __name__ == "__main__":
    neuron_name = pathlib.Path('/data/neural_collision_detection/data/neurons/AP120410_s1c1_balls.csv')
    alpha_shape, points = generate_alphashape_from_neuron(neuron_name)
    alphas = get_all_alpha_values(alpha_shape)
    print(f"Found {len(alphas)} alphas for neuron {neuron_name.name} which has {len(points)} points.")
    alphas = sample_alphas(alphas)
    all_dfs = []
    for alpha in alphas:
        print(alpha)
        all_dfs.append(process_single_alpha(alpha, alpha_shape, points))
    print("Concatenating")
    all_dfs = dask.delayed(pd.concat)(all_dfs, axis=1)

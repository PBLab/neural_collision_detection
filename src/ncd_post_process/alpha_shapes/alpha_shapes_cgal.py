"""
Main script to calculate the alpha values for the geometrical
shape of a neuron.
"""
import pathlib
import sys
from itertools import chain
import multiprocessing

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


sys.path.append(
    "/data/MatlabCode/PBLabToolkit/External/cgal-python-bindings/src/alpha3_bindings/delaunay_fast_location_release"
)
from tri3_epic import *

sys.path.pop(-1)


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
    alphas.pop(0)  # first val is always 0
    return alphas


def classify_points(shp: Alpha_shape_3, points: list, cls_dict: dict) -> np.ndarray:
    """Iterates over the points of the alpha shape and classifies them,
    returning a dict with their values."""
    classified = np.empty(len(points), dtype=np.int8)
    for idx, point in enumerate(points):
        classified[idx] = cls_dict[str(shp.classify(point))]
    return classified


def sample_alphas(alphas: np.ndarray, factor=10) -> np.ndarray:
    len_ = len(alphas)
    alphas = np.asarray(alphas)
    return alphas[np.linspace(0, len_ - 1, len_ // factor, dtype=np.uint32)]


def process_single_shape(neuron_name):
    """General alpha shape processing pipe"""
    foldername = pathlib.Path("/data/neural_collision_detection/data/neurons")
    ext = "_balls_yz_flipped.csv"
    full_neuron_name = foldername / (neuron_name + ext)
    alpha_shape, points = generate_alphashape_from_neuron(full_neuron_name)
    output_folder = pathlib.Path(
        "/data/neural_collision_detection/results/for_article/fig2"
    )
    alphas = get_all_alpha_values(alpha_shape)
    print(
        f"Found {len(alphas)} alphas for neuron {neuron_name} which has {len(points)} points."
    )
    alphas = sample_alphas(alphas)
    cls_dict = {
        "INTERIOR": np.int8(0),
        "EXTERIOR": np.int8(1),
        "REGULAR": np.int8(2),
        "SINGULAR": np.int8(3),
    }
    all_classifications = []
    for alpha in alphas:
        alpha_shape.set_alpha(alpha)
        classified = classify_points(alpha_shape, points, cls_dict)
        all_classifications.append(classified)
    all_classifications = pd.DataFrame(np.vstack(all_classifications).T, columns=alphas)
    all_classifications.attrs = {"neuron_name": neuron_name}
    all_classifications.to_hdf(output_folder / (neuron_name + "_alpha_distrib.h5"), key='data', complevel=3)


def find_first_interior_alpha_shape_value(alphas: pd.DataFrame) -> np.ndarray:
    """Finds the smallest alpha value that interiorized each point.

    When calculating alpha shapes, each point on the neuron is continuously
    checked for whether it's inside, on the edge, or outside the shape. The functions'
    goal is to detect the "transition" of each point from being on the outside of
    the shape (values of > 0) to being inside (value == 0).

    Parameters
    ----------
    alphas : pd.DataFrame
        Neural points are on the rows and alpha shape values are the columns

    Returns
    -------
    np.ndarray
        The alpha value for each neural point. NaN if it's never found inside
    """
    interior_alphas = np.where(alphas == 0)
    first_zeros = pd.DataFrame({"x": interior_alphas[0], "y": interior_alphas[1]})
    first_alpha = first_zeros.groupby("x").min()
    all_rows = np.full((alphas.shape[0],), np.nan)
    all_rows[first_alpha.index] = alphas.columns[first_alpha["y"]]
    return all_rows


if __name__ == "__main__":
    neuron_names = [
        # "AP120507_s3c1",
        # "AP131105_s1c1",
        # "AP120410_s1c1",
        # "AP120410_s3c1",
        # "AP120412_s3c2",
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
        "AP120507_s3c1",
        "MW120607_LH3",
    ]

    with multiprocessing.Pool() as mp:
        mp.map(process_single_shape, neuron_names)
    # for neuron in neuron_names[:1]:
    #     process_single_shape(neuron)

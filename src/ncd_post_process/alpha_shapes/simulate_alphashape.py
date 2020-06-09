import sys

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sys.path.append(
    "/data/MatlabCode/PBLabToolkit/External/cgal-python-bindings/src/alpha3_bindings/delaunay_fast_location_release"
)
from tri3_epic import *
sys.path.pop(-1)


def generate_points_and_alpha():
    """Simulates 3D points with their alpha shape.

    Returns
    -------
    points : np.ndarray
        n by 3 array of points
    shp : Alpha_shape_3
        Alpha shape for these points
    """
    points = [
        Point_3(0, 0, 1),
        Point_3(0, 0, 0.5),
        Point_3(-1, 0, 0),
        Point_3(1, 0, 0),
        Point_3(0, 1, 0),
        Point_3(0, -1, 0),
        Point_3(0, 0, 0),
        Point_3(0.25, 0.25, 0),
        Point_3(-0.25, 0.25, 0),
        Point_3(0.25, -0.25, 0),
        Point_3(-0.25, -0.25, 0),
    ]
    shp = Alpha_shape_3(points)
    return points, shp


def cgal_points_to_numpy(points: list) -> np.ndarray:
    """Converst a CGAL point array to a numpy array.

    Parameters
    ----------
    points : list of Point3
        A list of Point3 objects simulating a Nx3 array

    Returns
    -------
    np.ndarray
        N x 3 point array
    """
    return np.asarray([[p.x(), p.y(), p.z()] for p in points])


def find_crit_alpha_values_per_shape(shp: Alpha_shape_3) -> np.ndarray:
    """Returns all critical alpha values for given shape.

    The functions turns the first alpha value into a 0 as it is sometimes
    returns as a floating point value which is close to 0. It also appends a large
    alpha value to the end of the list to make sure that the final critical value
    is really all-encompassing.

    Parameters
    ----------
    shp: Alpha_shape_3
        Alpha shape to analyze

    Returns
    -------
    list
        A list of all alpha shapes critical values.
    """
    alphas = [shp.get_nth_alpha(idx) for idx in range(shp.number_of_alphas())]
    alphas[0] = 0.0
    alphas.append(100.0)
    return np.asarray(alphas)


def classify_points_per_alpha(
    shp: Alpha_shape_3, alphas: list, points: np.ndarray
) -> pd.DataFrame:
    """For each alpha value, find the classification of each point.

    The classification means whether the point is outside the shape, on
    its edge or inside.

    Parameters
    ----------
    shp : Alpha_shape_3
        Alpha shape object
    alphas : list
        List of critical alpha values
    points : np.ndarray
        The points composing that alpha object

    Returns
    -------
    pd.DataFrame
        A table where the columns are alpha values, and the rows are the points
    """
    columns = ['coord'] + list(alphas)
    classification = pd.DataFrame(
        np.empty((len(points), len(columns)), dtype=np.object), columns=columns
    )
    for alpha in alphas:
        shp.set_alpha(alpha)
        classification.loc[:, alpha] = [str(shp.classify(point)) for point in points]

    classification.loc[:, 'coord'] = points
    return classification


def scatter_3d_points_naive(points: np.ndarray):
    """Creates a 3D scatter plot of the given points"""
    figure = plt.figure()
    ax = figure.add_subplot(111, projection="3d")
    ax.scatter(points[:, 0], points[:, 1], points[:, 2])


def plot_classification_per_point_per_alpha(classification: pd.DataFrame):
    """Plots a figure with the points colored in colors labeling their
    location with the current alpha shape.

    Parameters
    ----------
    classification : pd.DataFrame
        points x alpha values table of classifications
    """
    colors = {
        Classification_type.EXTERIOR: "C1",
        Classification_type.INTERIOR: "C0",
        Classification_type.REGULAR: "C2",
    }

    figure = plt.figure()
    num_alphas = classification.shape[1]
    for idx, (alpha_val, data) in enumerate(classification.iteritems()):
        ax = figure.add_subplot(f"{num_alphas}1{idx + 1}", projection="3d")
        ax.scatter(data[:, 0], data[:, 1], data[:, 2])
        color_per_point = [colors[value] for value in data]
        ax.set_title(alpha_val)
    plt.show()


def run():
    points, shape = generate_points_and_alpha()
    alphas = find_crit_alpha_values_per_shape(shape)
    classification = classify_points_per_alpha(shape, alphas, points)
    # scatter_3d_points_naive(cgal_points_to_numpy(points))
    return points, shape, alphas, classification


if __name__ == "__main__":
    points, shape, alphas, classification = run()

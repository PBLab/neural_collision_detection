"""This module will calculate the distribution of distances between neuroons
and the surrounding vasculature for a given ("best") location and orientation
of that neuron.
"""
import pathlib
import multiprocessing

import dask.array as da
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import napari
import scipy.spatial
import numba

from ncd_post_process import db_to_dataframe


neuron_names = [
    "AP120410_s1c1",
    "AP120410_s3c1",
    "AP120412_s3c2",
    "AP120416_s3c1",
    "AP120419_s1c1",
    "AP120420_s1c1",
    "AP120420_s2c1",
    "AP120510_s1c1",
    "AP120522_s3c1",
    "AP120523_s2c1",
    "AP120524_s2c1",
    "AP120614_s1c2",
    "AP130110_s2c1",
    "AP130312_s1c1",
    "AP130606_s2c1",
    "AP131105_s1c1",
]


def load_csv_balls(fname: pathlib.Path) -> pd.DataFrame:
    """Loads a CSV file.

    Parameters
    ----------
    fname : pathlib.Path
        Data to parse

    Returns
    -------
    pd.DataFrame
        Parsed data
    """
    data = pd.read_csv(fname, header=None, names=['x', 'y', 'z', 'r'])
    return data


def swap_xy(df: pd.DataFrame):
    df = df.reindex(columns=['y', 'x', 'z', 'r'])
    return df.rename(columns={'y': 'x', 'x': 'y'})


def swap_xz(df: pd.DataFrame):
    df = df.reindex(columns=['z', 'y', 'x', 'r'])
    return df.rename(columns={'z': 'x', 'x': 'z'})


def find_best_orientation(coll_db: pathlib.Path) -> dict:
    colls = db_to_dataframe.read_db_into_raw_df(coll_db)
    colls = db_to_dataframe.parse_raw_df(colls)
    intcolls = db_to_dataframe.convert_to_int(colls)
    colls = db_to_dataframe.find_duplicate_colls(intcolls, colls)
    minimal_collision_orientation_location = colls.iloc[colls.index.get_level_values('coll_count').argmin()]
    return colls.loc[minimal_collision_orientation_location.name]


def rotate_table(data: pd.DataFrame, rotation: np.ndarray) -> pd.DataFrame:
    rotated = (rotation @ data.T).T
    return rotated


def translate_table(data: pd.DataFrame, translation: np.ndarray) -> pd.DataFrame:
    return data + translation


def generate_current_rotation(df: pd.DataFrame) -> np.ndarray:
    """Based on the current orientation of the neuron, generate a rotation
    matrix that will be used to rotate the collisions and neuron itself.

    The actual work of constructing the matrix is done in "make_rotation_matrix".

    Parameters
    ----------
    df : pd.DataFrame
        Collision data, which contains the rotation in its index

    Returns
    -------
    3x3 np.ndarray
        The rotation matrix
    """
    roll = df.index.get_level_values('roll')[0]
    pitch = df.index.get_level_values('pitch')[0]
    yaw = df.index.get_level_values('yaw')[0]
    rot_in_degrees = np.array([roll, pitch, yaw])
    return make_rotation_matrix(rot_in_degrees)


def make_rotation_matrix(rot: np.ndarray) -> np.ndarray:
    """Construct a standard rotation matrix from the given x-y-z rotation.

    Parameters
    ----------
    rot : np.ndarray
        len == 3 numpy array

    Returns
    -------
    np.ndarray
        3x3 rotation numpy array
    """
    rot_in_rads = np.radians(rot)
    sine, cosine = np.sin(rot_in_rads), np.cos(rot_in_rads)
    m_x = np.array([[1, 0, 0], [0, cosine[0], -sine[0]], [0, sine[0], cosine[0]]])
    m_y = np.array([[cosine[1], 0, sine[1]], [0, 1, 0], [-sine[1], 0, cosine[1]]])
    m_z = np.array([[cosine[2], -sine[2], 0], [sine[2], cosine[2], 0], [0, 0, 1]])
    rot_matrix = m_x @ m_y @ m_z
    return rot_matrix


def generate_current_translation(df: pd.DataFrame) -> np.ndarray:
    x = df.index.get_level_values('x')[0]
    y = df.index.get_level_values('y')[0]
    z = df.index.get_level_values('z')[0]
    return np.array([[x, y, z]], dtype=np.float64)


def rotate_and_translate(key_table: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
    """Iterates over the given data items and
    rotates and translates them according to the key.

    The items in the given list are assumed to be dataframes.

    Parameters
    ----------
    key_table : pd.DataFrame
        A table containing the needed translation and rotation information
        in its index.
    data : pd.DataFrame
        Item to rotate and translate independently

    Returns
    -------
    processed : pd.DataFrame
       Rotated and translated dataframe
    """
    rotation = generate_current_rotation(key_table)
    translation = generate_current_translation(key_table)
    data = data.iloc[:, :3]  # disregard radius
    rotated = rotate_table(data, rotation)
    translated = translate_table(rotated, translation)
    return translated


def get_subset_of_vasculature(neuron: np.ndarray, vasc: np.ndarray):
    maxs = neuron.max(axis=0) * 1.1
    mins = neuron.min(axis=0) * 0.9
    min_ = len(vasc)
    max_ = 0
    for idx, vasc_coords in enumerate(vasc.T):
        vasc_coords.compute_chunk_sizes()
        sect = np.logical_and(mins[idx] <= vasc_coords, vasc_coords <= maxs[idx])
        sect = np.where(sect)[0]
        sect.compute_chunk_sizes()
        if sect[0] < min_:
            min_ = sect[0]
        if sect[-1] > max_:
            max_ = sect[-1]

    return vasc[int(min_):int(max_), :].rechunk((10000, 3))


def single_neuron_pipeline(neuron_name: str, vascular_data: da.array):
    collisions_folder = pathlib.Path('/data/neural_collision_detection/results/2020_07_29/')
    collisions_fname = collisions_folder / f'agg_results_{neuron_name}_thresh_0.csv'
    neurons_folder = pathlib.Path('/data/neural_collision_detection/data/neurons')
    neuron_fname = neurons_folder / f'{neuron_name}_balls_yz_flipped.csv'
    raw_neuron_data = load_csv_balls(neuron_fname)
    colls = find_best_orientation(collisions_fname)
    processed_neuron = rotate_and_translate(colls, raw_neuron_data).to_numpy().astype(np.float32)
    vascular_data = get_subset_of_vasculature(processed_neuron, vascular_data).compute()
    distance_to_closest_vasc = find_closest_vasc_per_neuronal_point(processed_neuron, vascular_data)
    _, ax = plt.subplots()
    ax.hist(distance_to_closest_vasc, bins=100)
    ax.set_title(neuron_name)
    return distance_to_closest_vasc, colls


@numba.jit(nopython=True, parallel=True)
def find_closest_vasc_per_neuronal_point(processed_neuron, vascular_data):
    final_dists = np.zeros(len(processed_neuron), dtype=np.float32)
    range_on_vasc = range(len(vascular_data))
    for index in numba.prange(len(processed_neuron)):
        neural_coord = processed_neuron[index, :]
        current_min = np.float32(1000)
        for vasc_coord_idx in range_on_vasc:
            norm = np.linalg.norm(neural_coord - vascular_data[vasc_coord_idx, :])
            current_min = norm if norm < current_min else current_min
        final_dists[index] = current_min
    return final_dists


def viz_neurons_and_vasc(neuron_and_colls, vascular_data):
    with napari.gui_qt():
        viewer = napari.view_points(vascular_data[:, :3], size=vascular_data[:, 3], face_color='magenta', name='vasculature')
        for (neuron, coll), neuron_name in zip(neuron_and_colls, neuron_names):
            viewer.add_points(neuron.to_numpy(), size=3, name=f'{neuron_name}')
            viewer.add_points(coll.to_numpy(), size=3, face_color='g', name=f"{len(coll)} collisions ({neuron_name})")


def plot_distance_distribution(neuron_and_colls, vascular_data):
    for (neuron, _), neuron_name in zip(neuron_and_colls, neuron_names):
        neuron = da.from_array(neuron.to_numpy().astype(np.float32), chunks='auto')
        dists = da.map_blocks(scipy.spatial.distance.cdist, neuron, vascular_data).compute()
        distance_to_closest_vasc = dists.min(axis=1)
        _, ax = plt.subplots()
        ax.hist(distance_to_closest_vasc, bins=100)
        ax.set_title(neuron_name)


if __name__ == '__main__':
    vascular_fname = pathlib.Path('/data/neural_collision_detection/data/vascular/vascular_balls.csv')
    vascular_data = da.from_array(load_csv_balls(vascular_fname).to_numpy().astype(np.float32)[:, :3], chunks='auto')
    neuron_and_colls = [single_neuron_pipeline(neuron_name, vascular_data) for neuron_name in neuron_names]
    viz_neurons_and_vasc(neuron_and_colls, vascular_data)
    plt.show(block=False)

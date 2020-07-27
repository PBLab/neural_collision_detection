"""This module will calculate the distribution of distances between neuroons
and the surrounding vasculature for a given ("best") location and orientation
of that neuron.
"""
import pathlib

import numpy as np
import pandas as pd
import napari

from ncd_post_process import db_to_dataframe


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
    df.columns = ['y', 'x', 'z', 'r']
    return df.rename(columns={'y': 'x', 'x': 'y'})


def find_best_orientation(coll_db: pathlib.Path) -> dict:
    colls = db_to_dataframe.read_db_into_raw_df(coll_db)
    colls = db_to_dataframe.parse_raw_df(colls)
    colls = db_to_dataframe.find_duplicate_colls(colls)
    colls_per_rot = colls.groupby(['roll', 'pitch', 'yaw', 'coll_count']).count()
    minimal_coll_row_index = colls_per_rot.index.get_level_values('coll_count').argmin()
    index = colls_per_rot.iloc[minimal_coll_row_index].name[:3]
    idx = pd.IndexSlice
    rows = colls.loc[idx[:, :, :, :, :, :, index[0], index[1], index[2], :], :]
    return rows


def rotate_table(data: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    rotated = (rotation @ data.T).T
    return rotated


def translate_table(data: np.ndarray, translation: np.ndarray) -> np.ndarray:
    return data + translation


def compare_vasc_neuronal_dist():
    pass


def show_dist_distribution():
    pass


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


def rotate_and_translate(key_table: pd.DataFrame, data: list) -> list:
    """Iterates over the given data items and
    rotates and translates them according to the key.

    The items in the given list are assumed to be dataframes.

    Parameters
    ----------
    key_table : pd.DataFrame
        A table containing the needed translation and rotation information
        in its index.
    data : list of pd.DataFrame
        Items to rotate and translate independently

    Returns
    -------
    processed : list of pd.DataFrame
        Same length as input, same shape of item
    """
    result = []
    rotation = generate_current_rotation(key_table)
    translation = generate_current_translation(key_table)
    for item in data:
        item = item[:, :3]  # disregard radius
        rotated = rotate_table(item, rotation)
        translated = translate_table(rotated, translation)
        result.append(translated)
    return result


if __name__ == '__main__':
    neuron_name = pathlib.Path('AP120410_s1c1')
    neurons_folder = pathlib.Path('/data/neural_collision_detection/data/neurons/')
    neuron_fname = neurons_folder / f'{neuron_name}_balls.csv'
    vascular_fname = pathlib.Path('/data/neural_collision_detection/data/vascular/vascular_balls.csv')
    collisions_fname = pathlib.Path('/data/neural_collision_detection/results/2020_02_14/agg_results_AP120410_s1c1_thresh_0.csv')
    raw_neuron_data = load_csv_balls(neuron_fname)
    raw_neuron_data = swap_xy(raw_neuron_data).iloc[:, :3].to_numpy()
    colls = find_best_orientation(collisions_fname)
    result = rotate_and_translate(colls, [raw_neuron_data])
    neuron_data = result[0]
    with napari.gui_qt():
        viewer = napari.view_points(neuron_data, size=3)
        viewer.add_points(colls, size=3, face_color='g', name="collisions")
        # viewer.add_points(raw_neuron_data, size=3, face_color='y', name="raw_neuron")
        # viewer.add_points(vascular_data[:, :3], size=vascular_data[:, 3], face_color='magenta', name='vasculature')


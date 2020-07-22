"""This module will calculate the distribution of distances between neuroons
and the surrounding vasculature for a given ("best") location and orientation
of that neuron.
"""
import pathlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ncd_post_process import db_to_dataframe


def load_csv_balls(fname: pathlib.Path) -> pd.DataFrame:
    """Loads a CSV file and swaps its x-y columns.

    Since every CSV file we have has its x-y coordinates
    swapped, we always wish to swap the coordinates before 
    returning the data to the user.
    
    Parameters
    ----------
    fname : pathlib.Path
        Data to parse

    Returns
    -------
    pd.DataFrame
        Parsed data
    """
    data = pd.read_csv(fname, header=None, names=['y', 'x', 'z', 'r'])
    data.columns = ['x', 'y', 'z', 'r']
    return data


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


def rotate_table(data: pd.DataFrame, rotation: np.ndarray) -> pd.DataFrame:
    rotated = (rotation @ data.T).T
    rotated[0], rotated[1] = rotated[1], rotated[0].copy()
    return rotated


def translate_table(data: pd.DataFrame, translation: np.ndarray) -> pd.DataFrame:
    return data - translation


def compare_vasc_neuronal_dist():
    pass


def show_dist_distribution():
    pass


def generate_current_rotation(df: pd.DataFrame) -> np.ndarray:
    """Based on the current orientation of the neuron, generate a rotation
    matrix that will be used to rotate the collisions and neuron itself.

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
    rot_in_rads = np.radians([roll, pitch, yaw])
    sine, cosine = np.sin(rot_in_rads), np.cos(rot_in_rads)
    m_x = np.array([[1, 0, 0], [0, cosine[0], -sine[0]], [0, sine[0], cosine[0]]])
    m_y = np.array([[cosine[1], 0, sine[1]], [0, 1, 0], [-sine[1], 0, cosine[1]]])
    m_z = np.array([[cosine[2], -sine[2], 0], [sine[2], cosine[2], 0], [0, 0, 1]])
    rot_matrix = np.linalg.inv(m_x @ m_y @ m_z)
    return rot_matrix


def generate_current_translation(df: pd.DataFrame) -> np.ndarray:
    x = df.index.get_level_values('x')
    y = df.index.get_level_values('y')
    z = df.index.get_level_values('z')
    return np.ndarray([[x, y, z]])


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
    neuron_data = load_csv_balls(neuron_fname)
    colls = find_best_orientation(collisions_fname)
    result = rotate_and_translate(colls, [neuron_data, colls])
    neuron_data, colls = result
    # vascular_data = load_csv_balls(vascular_fname)
    # rotated_neuron = rotate_neuron(neuron_data)
    # translated_neuron = translate_neuron(rotated_neuron)


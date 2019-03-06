import multiprocessing
import pathlib
import multiprocessing as mp

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numba
import scipy.io


def read_db_into_raw_df(fname) -> pd.DataFrame:
    """
    Basic functionality to read the current
    DB format into an unprocessed DataFrame.
    """
    column_names = ['run_id', 'neuron', 'vasc', 'location', 'rotation', 'coll_count', 'collisions']
    dtypes = {column_names[0]: 'category', column_names[1]: 'category',
              column_names[2]: 'category', column_names[3]: str, column_names[4]: str,
              column_names[5]: int, column_names[6]: str}
    df = pd.read_csv(fname, header=None, names=column_names,
                     index_col=column_names[:3], dtype=dtypes)
    return df


def parse_raw_df(df) -> pd.DataFrame:
    """
    Interprets the raw DF generated by "read_db_into_raw_df" into a
    MultiIndex DataFrame, each value being an x-y-z coordinate of
    a collision.
    """

    # Parse "location" into three (x, y, z) columns

    locs = (df
        .location
        .str.split(' ', expand=True)
        .rename(columns={0: 'x', 1: 'y', 2: 'z'})
        .astype(np.float64))
    df[['x', 'y', 'z']] = locs
    df = df.drop('location', axis=1)

    # Parse "rotation" into three (roll, yaw, pitch) columns
    rots = (df
        .rotation
        .str.split(' ', expand=True)
        .rename(columns={0: 'roll', 1: 'pitch', 2: 'yaw'})
        .astype(np.float64))

    df[['roll', 'pitch', 'yaw']] = rots
    df = df.drop('rotation', axis=1)
    index_cols = list(set(df.columns) - set(['collisions']))
    ordered_index_cols = ['x', 'y', 'z', 'roll', 'pitch', 'yaw', 'coll_count']
    assert set(ordered_index_cols) == set(index_cols)
    df.set_index(ordered_index_cols, inplace=True, append=True)

    # Parse collision coordinates into a new DataFrame, x-y-z as columns and the neuron name
    # as a categorical index
    print("Parsing collisions...")
    cols_list = []
    for idx, data in df.collisions.items():
        try:
            split = data.replace('|', ' ').split(' ')
        except AttributeError:  # no collisions
            arr = np.array([[np.nan, np.nan, np.nan]], dtype=np.float64)
        else:
            assert len(split) % 3 == 0  # x-y-z coords
            arr = np.array(split, dtype=np.float64).reshape((-1, 3))
        index_dict = {k: v for k, v in zip(df.index.names, idx)}
        new_df = pd.DataFrame({'coll_x': arr[:, 0], 'coll_y': arr[:, 1], 'coll_z': arr[:, 2],
                               **index_dict})
        cols_list.append(new_df)

    collisions = pd.concat(cols_list)

    for col_name in ['run_id', 'neuron', 'vasc']:
        collisions[col_name] = collisions[col_name].astype('category')
    collisions = collisions.set_index(df.index.names)

    return collisions


def get_stats(df: pd.DataFrame):
    rows = np.linspace(10000, 25000, 10, dtype=np.uint64)
    collisions_df = df.iloc[rows, :]
    chosen_pos = np.array([collisions_df.index.get_level_values('x'),
                           collisions_df.index.get_level_values('y'),
                           collisions_df.index.get_level_values('z')]).T


    idx = pd.IndexSlice
    relevant_collisions = df.loc[idx[:, :, :, chosen_pos[:, 0],
                                     chosen_pos[:, 1], chosen_pos[:, 2], :, :, :, :],
                                 :]
    color_dict = {tuple(row): f'C{idx}' for idx, row in enumerate(chosen_pos)}
    relevant_collisions['color'] = color_dict[tuple(relevant_collisions.loc[:, 'x':'z'])]
    return chosen_pos, relevant_collisions


def translate_colls(colls):
    """ Translates the collisions back to the original coordinates """
    colls_translated = colls.values
    colls_translated[:, 0] -= colls.index.get_level_values('x')
    colls_translated[:, 1] -= colls.index.get_level_values('y')
    colls_translated[:, 2] -= colls.index.get_level_values('z')
    return colls_translated


def rotate_colls(colls: pd.DataFrame, colls_translated: np.ndarray) -> np.ndarray:
    """ Rotates the translated collisions """
    rot = np.stack((
        colls.index.get_level_values('roll').values,
        colls.index.get_level_values('pitch').values,
        colls.index.get_level_values('yaw').values,
    ), axis=1)
    # with multiprocessing.Pool() as pool:
    #     rotated_colls = pool.starmap(_rotate_single_coll, zip(rot, colls_translated))
    rotated_colls = [_rotate_single_coll(rotx, coll) for rotx, coll in zip(rot, colls_translated)]
    return np.array(rotated_colls)


def _rotate_single_coll(rot: np.ndarray, coll: np.ndarray) -> np.ndarray:
    """ Rotates a collisions 3D coordinate coll by rot degrees
    in each axis.
    rot is a vector with three entries, angle per axis.
    coll is a vector with three entries, identifying the coordinates of
    a specific collision.
    """
    rot_in_rads = np.radians(rot)
    sine, cosine = np.sin(rot_in_rads), np.cos(rot_in_rads)
    m_x = np.array([[1, 0, 0],
                    [0, cosine[0], -sine[0]],
                    [0, sine[0], cosine[0]]])
    m_y = np.array([[cosine[1], 0, sine[1]],
                    [0, 1, 0],
                    [-sine[1], 0, cosine[1]]])
    m_z = np.array([[cosine[2], -sine[2], 0],
                    [sine[2], cosine[2], 0],
                    [0, 0, 1]])
    rot_matrix = np.linalg.inv(m_x @ m_y @ m_z)
    rotated_colls = (rot_matrix @ coll.T).T
    rotated_colls[0], rotated_colls[1] = rotated_colls[1], rotated_colls[0].copy()
    return rotated_colls


def save_results(data_dict, fname: pathlib.Path):
    """ Save results into file in numpy and MATLAB formats """
    np.savez(str(fname.with_suffix('.npz')), **data_dict)
    scipy.io.savemat(str(fname.with_suffix('.mat')), data_dict)


def mp_run(parent_folder: pathlib.Path, fname: pathlib.Path):
    """
    Wrapper script to run this module on multiple cores
    """
    raw_df = read_db_into_raw_df(fname)
    cols = parse_raw_df(raw_df)
    colls_translated = translate_colls(cols)
    colls_trans_rot = rotate_colls(cols, colls_translated)
    new_fname = pathlib.Path("normalized_" + fname.name)
    save_results({'neuron_coords': colls_trans_rot, 'vasc_coords': cols}, parent_folder / new_fname)


if __name__ == '__main__':
    parent_folder = pathlib.Path(r'/data/simulated_morph_data/results/2019_2_10/')
    all_args = [(parent_folder, file) for file in parent_folder.glob('agg_results_*_thresh_0')]
    with mp.Pool() as pool:
        pool.starmap(mp_run, all_args)


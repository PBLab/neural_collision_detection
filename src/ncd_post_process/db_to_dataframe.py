import multiprocessing
import pathlib
import multiprocessing as mp

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
    column_names = [
        "run_id",
        "neuron",
        "vasc",
        "location",
        "rotation",
        "coll_count",
        "collisions",
    ]
    dtypes = {
        column_names[0]: "category",
        column_names[1]: "category",
        column_names[2]: "category",
        column_names[3]: str,
        column_names[4]: str,
        column_names[5]: int,
        column_names[6]: str,
    }
    df = pd.read_csv(
        fname, header=None, names=column_names, index_col=column_names[:3], dtype=dtypes
    )
    return df


def parse_raw_df(df) -> pd.DataFrame:
    """
    Interprets the raw DF generated by "read_db_into_raw_df" into a
    MultiIndex DataFrame, each value being an x-y-z coordinate of
    a collision.

    The function also does two important things implicitly:
    First, it rounds the floating-point coordinates of the collisions
    into the nearest integer,
    """

    # Parse "location" into three (x, y, z) columns

    locs = (
        df.location.str.split(" ", expand=True)
        .rename(columns={0: "x", 1: "y", 2: "z"})
        .astype(np.float64)
    )
    df[["x", "y", "z"]] = locs
    df = df.drop("location", axis=1)

    # Parse "rotation" into three (roll, yaw, pitch) columns
    rots = (
        df.rotation.str.split(" ", expand=True)
        .rename(columns={0: "roll", 1: "pitch", 2: "yaw"})
        .astype(np.float64)
    )

    df[["roll", "pitch", "yaw"]] = rots
    df = df.drop("rotation", axis=1)
    index_cols = list(set(df.columns) - set(["collisions"]))
    ordered_index_cols = [
        "x",
        "y",
        "z",
        "roll",
        "pitch",
        "yaw",
        "coll_count",
    ]
    assert set(ordered_index_cols) == set(index_cols)
    df.set_index(ordered_index_cols, inplace=True, append=True)

    # Parse collision coordinates into a new DataFrame, x-y-z as columns and the neuron name
    # as a categorical index
    print("Parsing collisions...")
    cols_list = []
    for idx, data in df.collisions.items():
        try:
            split = data.replace("|", " ").split(" ")
        except AttributeError:  # no collisions
            arr = np.array([[np.nan, np.nan, np.nan]], dtype="float64")
        else:
            assert len(split) % 3 == 0  # x-y-z coords
            arr = np.array(split, dtype="float64").reshape((-1, 3))
        index_dict = {k: v for k, v in zip(df.index.names, idx)}
        new_df = pd.DataFrame(
            {
                "coll_x": arr[:, 0],
                "coll_y": arr[:, 1],
                "coll_z": arr[:, 2],
                **index_dict,
            }
        )
        cols_list.append(new_df)

    collisions = pd.concat(cols_list)

    for col_name in ["run_id", "neuron", "vasc"]:
        collisions[col_name] = collisions[col_name].astype("category")
    collisions = collisions.set_index(df.index.names)

    return collisions


def get_stats(df: pd.DataFrame):
    rows = np.linspace(10000, 25000, 10, dtype=np.uint64)
    collisions_df = df.iloc[rows, :]
    chosen_pos = np.array(
        [
            collisions_df.index.get_level_values("x"),
            collisions_df.index.get_level_values("y"),
            collisions_df.index.get_level_values("z"),
        ]
    ).T

    idx = pd.IndexSlice
    relevant_collisions = df.loc[
        idx[:, :, :, chosen_pos[:, 0], chosen_pos[:, 1], chosen_pos[:, 2], :, :, :, :],
        :,
    ]
    color_dict = {tuple(row): f"C{idx}" for idx, row in enumerate(chosen_pos)}
    relevant_collisions["color"] = color_dict[
        tuple(relevant_collisions.loc[:, "x":"z"])
    ]
    return chosen_pos, relevant_collisions


def convert_to_int(colls: pd.DataFrame):
    for column in ['x', 'y', 'z']:
        as_int = colls.loc[:, f'coll_{column}'].to_numpy().astype('int32', casting='unsafe')
        colls.loc[:, f'coll_{column}'] = as_int
    return colls


def find_duplicate_colls(intcol: pd.DataFrame, colls: pd.DataFrame):
    """Iterates over the DataFrame and finds locations which were registered
    as having multiple collisions, while in effect they only had one collision,
    but it was registered as more due to issues with the brute-force calc and our
    actual resolution, which is on the order of 1 um.

    This function will also change the coll_count to match the new value.

    Returns a filtered DF not containing these rows.
    """
    non_dup_df = []
    for ((_, intgroup), (_, realgroup)) in zip(intcol.groupby(['x', 'y', 'z']), colls.groupby(['x', 'y', 'z'])):
        _, index = np.unique(intgroup.to_numpy(), return_index=True, axis=0)
        relevant_rows = realgroup.iloc[index, :].reset_index(level='coll_count')
        relevant_rows.loc[:, 'coll_count'] = len(relevant_rows)
        relevant_rows = relevant_rows.set_index('coll_count', append=True)
        non_dup_df.append(relevant_rows)

    return pd.concat(non_dup_df)


def translate_colls(colls) -> np.ndarray:
    """ Translates the collisions back to the original coordinates """
    colls_translated = colls.to_numpy()
    colls_translated[:, 0] -= colls.index.get_level_values("x")
    colls_translated[:, 1] -= colls.index.get_level_values("y")
    colls_translated[:, 2] -= colls.index.get_level_values("z")
    return colls_translated


def rotate_colls(colls: pd.DataFrame, colls_translated: np.ndarray) -> np.ndarray:
    """ Rotates the translated collisions """
    rot = np.stack(
        (
            colls.index.get_level_values("roll").to_numpy(),
            colls.index.get_level_values("pitch").to_numpy(),
            colls.index.get_level_values("yaw").to_numpy(),
        ),
        axis=1,
    )
    rotated_colls = [
        _rotate_single_coll(rotx, coll) for rotx, coll in zip(rot, colls_translated)
    ]
    return rotated_colls


def _rotate_single_coll(rot: np.ndarray, coll: np.ndarray) -> np.ndarray:
    """ Rotates a collisions 3D coordinate coll by rot degrees
    in each axis.
    rot is a vector with three entries, angle per axis.
    coll is a vector with three entries, identifying the coordinates of
    a specific collision.
    """
    rot_in_rads = np.radians(rot)
    sine, cosine = np.sin(rot_in_rads), np.cos(rot_in_rads)
    m_x = np.array([[1, 0, 0], [0, cosine[0], -sine[0]], [0, sine[0], cosine[0]]])
    m_y = np.array([[cosine[1], 0, sine[1]], [0, 1, 0], [-sine[1], 0, cosine[1]]])
    m_z = np.array([[cosine[2], -sine[2], 0], [sine[2], cosine[2], 0], [0, 0, 1]])
    rot_matrix = np.linalg.inv(m_x @ m_y @ m_z)
    rotated_colls = (rot_matrix @ coll.T).T
    rotated_colls[0], rotated_colls[1] = rotated_colls[1], rotated_colls[0].copy()
    return rotated_colls


def save_results(
    fname: pathlib.Path,
    colls_trans_rot: np.ndarray,
    cols: np.ndarray,
    unique_collisions: np.ndarray,
    prob: np.ndarray,
    num_of_locs: int,
):
    """ Save results into file in numpy and MATLAB formats """
    data_dict = (
        {
            "neuron_coords": np.asarray(colls_trans_rot),
            "vasc_coords": np.asarray(cols),
            "unique_coords": unique_collisions,
            "coll_prob": prob,
            "num_of_locs": num_of_locs,
        }
    )
    np.savez(str(fname.with_suffix(".npz")), **data_dict)
    scipy.io.savemat(str(fname.with_suffix(".mat")), data_dict)


def count_collisions(colls, num_of_locs: int):
    """Find the number of unique collisions and of their occurrences.

    A collision location, i.e. the 3D coordinate in which a blood vessel met a neuron,
    isn't necessarily unique across all neuron locations. If we wish to know the
    probability that a collision will happen in a certain location, we have to count the
    number of times a collision occurred in this location, and then divide it by
    the number of locations (`num_of_locs`) that this neuron was placed in.

    This function returns an array in which the first row is the hash of the collision
    coordinate, and the row column is the chance for a collision in that coordinate,
    after the normalization process. This is basically a dictionary, mapping a collision
    location to its probability of collision.

    Note: the return type is an array because it will be written to disk in .npy format.
    """
    uniques, counts = np.unique(
        colls, return_counts=True, axis=0
    )
    return uniques, counts / num_of_locs


def mp_run(parent_folder: pathlib.Path, fname: pathlib.Path):
    """ Wrapper script to run this module on multiple cores """
    print(fname)
    raw_df = read_db_into_raw_df(fname)
    cols = parse_raw_df(raw_df)
    intcols = convert_to_int(cols)
    cols = find_duplicate_colls(intcols, cols)
    colls_translated = translate_colls(cols)
    colls_trans_rot = np.asarray(rotate_colls(cols, colls_translated))
    colls_trans_rot = colls_trans_rot.astype('int32')
    num_of_locs = len(raw_df)
    unique_collisions, prob = count_collisions(colls_trans_rot, num_of_locs)
    new_fname = pathlib.Path("normalized_" + fname.name)
    save_results(
        parent_folder / new_fname,
        np.asarray(colls_trans_rot),
        np.asarray(cols).astype('int32'),
        unique_collisions,
        prob,
        len(raw_df),
    )
    return colls_trans_rot


if __name__ == "__main__":
    parent_folder = pathlib.Path(r"/data/neural_collision_detection/results/2020_09_05")
    all_args = [
        (parent_folder, file)
        for file in parent_folder.glob("agg_results_*thresh_0.csv")
    ]
    with mp.Pool() as pool:
        colls = pool.starmap(mp_run, all_args)
    # colls = mp_run(*all_args[1])

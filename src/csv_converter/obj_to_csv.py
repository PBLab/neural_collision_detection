import pathlib

import pandas as pd


def load_verts_from_obj(fname: pathlib.Path):
    return pd.read_csv(fname, sep=' ', header=None, index_col=0, names=['h', 'x', 'y', 'z']).loc['v', :].reset_index().loc[:, "x":"z"]


def load_original_balls(fname: pathlib.Path):
    return pd.read_csv(fname, header=None, names=['x', 'y', 'z', 'r'])


def get_neuron_name(fname: pathlib.Path):
    return '_'.join(fname.name.split('_')[:2])


if __name__ == '__main__':
    foldername = pathlib.Path('/data/neural_collision_detection/data/neurons')
    for file in foldername.glob("*balls.csv"):
        balls = load_original_balls(file)
        neuron_name = get_neuron_name(file)
        neuron_name = pathlib.Path(f'/data/neural_collision_detection/src/convert_obj_matlab/{neuron_name}_yz_flipped.obj')
        verts = load_verts_from_obj(neuron_name)
        verts.loc[:, "r"] = balls.loc[:, "r"]
        new_fname = foldername / (file.stem + "_yz_flipped.csv")
        verts.to_csv(new_fname, header=None, index=False)


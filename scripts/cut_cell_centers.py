"""
Extracts the relevant layers from the neuron centers csv file
into different files
"""
from enum import Enum
import pandas as pd
import numpy as np


class CorticalLayer(Enum):
    ONE = (0, 80)
    TWOTHREE = (80, 350)
    FOUR = (350, 500)
    FIVE = (500, 850)
    SIX = (850, 1250)


def read_csv(fname, downsample=1):
    data = pd.read_csv(fname, header=None, names=['x', 'y', 'z'])
    data = data.iloc[::downsample, :]
    return data


def get_neurons_from_layer(data: pd.DataFrame, layer: CorticalLayer):
    relevant_rows = (data['z'] >= layer.value[0]) & (data['z'] < layer.value[1])
    data = data.loc[relevant_rows, :]
    return data


if __name__ == "__main__":
    fname = '/data/simulated_morph_data/vascular/all_cell_centers.csv'
    data = read_csv(fname, downsample=1)
    for layer in [CorticalLayer.ONE, CorticalLayer.TWOTHREE,
                  CorticalLayer.FOUR, CorticalLayer.FIVE,
                  CorticalLayer.SIX]:
        cur_data = get_neurons_from_layer(data, layer)
        cur_data.to_csv(f'centers_layer_{layer.name}.csv')
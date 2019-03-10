"""
Extracts the relevant layers from the neuron centers csv file
into different files
"""
from enum import Enum
import pandas as pd
import numpy as np


class CorticalLayer(Enum):
    """ Depth of cortical layers in um """

    ONE = (0, 80)
    TWOTHREE = (80, 350)
    FOUR = (350, 500)
    FIVE = (500, 850)
    SIX = (850, 1250)


def read_csv(fname):
    data = pd.read_csv(fname, header=None, names=["x", "y", "z"])
    return data


def get_neurons_from_layer(data: pd.DataFrame, layer: CorticalLayer):
    relevant_rows = (data["z"] >= layer.value[0]) & (data["z"] < layer.value[1])
    data = data.loc[relevant_rows, :]
    return data


def save_cell_centers_array(
    data: pd.DataFrame, layer: CorticalLayer, num_to_save: int = 10000
):
    num_to_save = min(num_to_save, data.shape[0])
    indices = np.random.choice(data.shape[0], num_to_save, replace=False)
    data = data.iloc[indices, :]
    data.to_csv(f"centers_layer_{layer.name}.csv", header=None, index=False)


if __name__ == "__main__":
    fname = "/data/simulated_morph_data/vascular/all_cell_centers.csv"
    data = read_csv(fname)
    for layer in [
        CorticalLayer.ONE,
        CorticalLayer.TWOTHREE,
        CorticalLayer.FOUR,
        CorticalLayer.FIVE,
        CorticalLayer.SIX,
    ]:
        cur_data = get_neurons_from_layer(data, layer)
        save_cell_centers_array(cur_data, layer)


"""
This script was run only once, and populated all
of the needed manual entries in the database. In case
we delete some table it should be run again.
"""
from dj_tables import *


def drop_all():
    """
    Removes all manual tables
    """
    vasc = VasculatureData()
    vasc.drop_quick()
    cells = CellCenters()
    cells.drop_quick()
    neuron = Neuron()
    neuron.drop_quick()


def populate_vasc():
    vasc = VasculatureData()
    vasc.insert1((0, '../data/vascular/vascular.0.999.obj'))


def populate_cell_centers():
    cells = CellCenters()
    cells.insert1((0, 0, '../data/vascular/centers_layer_ONE.csv', 'I'))
    cells.insert1((1, 0, '../data/vascular/centers_layer_TWOTHREE.csv', 'II_III'))
    cells.insert1((2, 0, '../data/vascular/centers_layer_FOUR.csv', 'IV'))
    cells.insert1((3, 0, '../data/vascular/centers_layer_FIVE.csv', 'V'))
    cells.insert1((4, 0, '../data/vascular/centers_layer_SIX.csv', 'VI'))


def populate_neurons():
    neuron = Neuron()
    neuron_names = [
        "AP120410_s1c1",
        "AP120410_s3c1",
        "AP120412_s3c2",
        "AP120416_s3c1",
        "AP120419_s1c1",
        "AP120420_s1c1",
        "AP120420_s2c1",
        "AP120507_s3c1",
        "AP120510_s1c1",
        "AP120522_s3c1",
        "AP120524_s2c1",
        "AP120614_s1c2",
        "AP130312_s1c1",
        "AP131105_s1c1",
    ]
    layers = [
        ("V", 3),
        ("V", 3),
        ("V", 3),
        ("IV", 2),
        ("VI", 4),
        ("IV", 2),
        ("II_III", 1),
        ("II_III", 1),
        ("II_III", 1),
        ("I", 0),
        ("II_III", 1),
        ("V", 3),
        ("II_III", 2),
        ("II_III", 2),
    ]
    assert len(neuron_names) == len(layers)
    for idx, (neuron_name, layer) in enumerate(zip(neuron_names, layers)):
        fname = f'../data/neurons/{neuron_name}.xml'
        neuron.insert1((idx, neuron_name, fname, layer[0], layer[1], 0))


if __name__ == "__main__":
    # drop_all()
    populate_vasc()
    populate_cell_centers()
    populate_neurons()
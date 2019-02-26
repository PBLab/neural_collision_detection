"""
Assortment of functions that are usually called
whenever we deal with visualization in Blender.
"""
import numpy as np


def name_neuron_trees():
    """ Find the names Blender uses for the axon and dendrites """
    assert neuron[0]
    basic_tree_names = []
    for tree in neuron[0].tree:
        basic_tree_names.append(tree.type)
    real_tree_names = []
    idx_axon = 1
    idx_dendrite = 1
    for treename in basic_tree_names:
        if treename not in real_tree_names:
            real_tree_names.append(treename)
            continue
        if 'Axon' == treename:
            new_name = f'Axon.00{idx_axon}'
            idx_axon += 1
        elif 'Dendrite' == treename:
            new_name = f'Dendrite.00{idx_dendrite}'
            idx_dendrite += 1
        real_tree_names.append(new_name)
    return real_tree_names


def generate_color_codes(data):
    """
    Decide on the color value of each point in the neuron. This
    values is proportionate to the value of data in that point.
    """
    colorcodes = np.zeros((data.shape[0], 3))
    normed_data = (
        data / data.max()
    )
    colorcodes[:, 0] = normed_data
    colorcodes[:, 2] = 1 - normed_data
    return colorcodes
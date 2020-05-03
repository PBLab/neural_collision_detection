"""This module calculates the alpha-shape values for points
which belong to either the dendrite or axon, and tries to find
pairs of nearby axon-dendrite points which are differnet in
their collision numbers or in their alpha shape maximal
value.
"""
import pathlib

import pandas as pd
import numpy as np


def generate_df_from_neuron(fname: pathlib.Path) -> pd.DataFrame:
    """Creates a dataframe which contains the neural points and an index values
    hinting whether the point belongs to the axon or the dendrite.

    Parameters
    ----------
    fname : pathlib.Path
        [description]

    Returns
    -------
    pd.DataFrame
        [description]
    """

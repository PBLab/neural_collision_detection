"""
This file is design to plot the radius ("width", "thickness") of points on a neural tree
as a function of their collision probability, as well as perhaps other independent variables.
"""

import pathlib

import pandas as pd
import networkx as nx
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from ncd_post_process.graph_parsing import load_neuron
from ncd_post_process.graph_parsing import CollisionNode


def load_graph(fname: pathlib.Path):
    """Loads a graph representation of a neuron."""
    try:
        graph = nx.readwrite.gml.read_gml(
                str(fname), destringizer=CollisionNode.from_str
                )
    except FileNotFoundError:
        raise
    return graph


def extract_collision_radius_from_graph(g: nx.Graph) -> pd.DataFrame:
    """Iterates over a graph and extracts some properties of it to a
    DataFrame."""
    num_of_nodes = g.number_of_nodes()
    columns = ['dist_to_body', 'radius', 'collision', 'tree_type']
    data = pd.DataFrame(np.zeros((num_of_nodes, len(columns))), columns=columns)
    for row, node in enumerate(g.nodes()):
        data.iloc[row, :] = (node.dist_to_body, node.radius, node.collision_chance, node.tree_type)
    return data


def plot_radius_colls(df):
    """Plots the radius vs collision in the given dataframe."""
    sns.relplot(data=df, x='radius', y='collision', col='tree_type')


if __name__ == '__main__':
    graph_name = pathlib.Path('/data/neural_collision_detection/results/2020_02_14/graph_AP120410_s1c1_with_collisions.gml')
    g = load_graph(graph_name)
    data = extract_collision_radius_from_graph(g)
    plot_radius_colls(data)
    plt.show()


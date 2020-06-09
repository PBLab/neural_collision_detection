import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pathlib
import seaborn as sns


def load_obj(fname: pathlib.Path):
    data = pd.read_csv(fname, sep=' ', header=None, index_col=0, names=['h', 'x', 'y', 'z'])
    vertices = data.loc['v', :]
    vertices = vertices.reset_index()
    vertices = vertices.sort_values('x')
    return vertices


def load_points(fname: pathlib.Path):
    data = pd.read_csv(fname, header=None, names=['y', 'x', 'z', 'r'])
    data = data.sort_values('x')
    return data


def plot_data(data: pd.DataFrame):
    sns.scatterplot(data=data, x='idx', y='x', hue='origin')


if __name__ == '__main__':
    fname = '/data/neural_collision_detection/data/neurons/AP120410_s1c1.obj'
    fname_pts = '/data/neural_collision_detection/data/neurons/AP120410_s1c1_balls.csv'
    verts = load_obj(fname)
    verts['origin'] = 'o'
    data = load_points(fname_pts)
    data['origin'] = 'p'
    data = pd.concat([verts, data], ignore_index=True)
    data['idx'] = np.arange(len(data))
    plot_data(data)
    plt.show()

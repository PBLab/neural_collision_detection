"""
In order to run NCD we need to feed it with center points to place the neuron in.
But in order to generate these center points for the toy data we have to find its borders first,
So this is what this code does, by parsing the .csv files and writing out random
cell centers in its borders.
"""

import pandas as pd

vasc_fname = '/data/neural_collision_detection/yoav/new/artificial_vascular.csv'
df = pd.read_csv(vasc_fname, header=None)
for col in df.columns:
    print(f"min: {df[col].min()}, max: {df[col].max()}")

# The result is that the vasculature span from 0 to 1000 units
# in all directions. We now sample it and write to disk

sampled = df.sample(n=10_000, random_state=4).iloc[:, :3]
sampled.to_csv('/data/neural_collision_detection/results/for_article/fig1/random_cell_centers.csv', index=False, header=None)
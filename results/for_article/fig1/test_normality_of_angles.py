"""
This code runs the Shapiro-Wilk test on the raw data captured by NCD
after rotating the toy example of the blood vessels and box,
and verifies that the data is indeed distributed normally.

It goes hand in hand with the code in "plot_rotation_distances.py".
"""

import pandas as pd
import scipy.stats

fname = 'results/for_article/fig1/rotation_distances.csv'

data = pd.read_csv(fname, index_col=0)
relevant_columns = [
    data.loc["x distances", :].iloc[1, :],
    data.loc["y distances", :].iloc[1, :],
    data.loc["z distances", :].iloc[1, :],
    data.loc["Aggregated", :].iloc[1, :],
]
stats = []
for column in relevant_columns:
    stats.append(scipy.stats.shapiro(column))

print(stats)
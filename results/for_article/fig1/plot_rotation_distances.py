import pandas as pd
"""
In figure 1 we show how rotating the toy case vasculature has a known effect on the collisions
found by NCD. This code reads the raw data from the rotations and plots it
so that it could be displayed in a panel.

The same data is used in "test_normality_of_angles.py".
"""

import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt


fname = "results/for_article/fig1/rotation_distances.csv"

raw_data = pd.read_csv(fname, index_col=0, names=np.arange(-16, 17, step=1, dtype=np.int64), skiprows=[0])
relevant = pd.DataFrame(
    {
        "x": raw_data.loc["x distances", :].iloc[1, :],
        "y": raw_data.loc["y distances", :].iloc[1, :],
        "z": raw_data.loc["z distances", :].iloc[1, :],
        "Aggregate": raw_data.loc["Aggregated", :].iloc[1, :],
        "Angle [°]": raw_data.columns,
    }
)
ax = relevant.plot(x="Angle [°]", xlim=[-11, 11])
origin = matplotlib.lines.Line2D([0, 0], [0, 0.8], lw=1, ls='--', color='C5')
ax.add_line(origin)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylabel("Angle difference [°]")
ax.figure.savefig("a.pdf", transparent=True, dpi=300)
plt.show()
# sns.set(style="white", rc={"axes.facecolor": (0, 0, 0, 0)})

# # Initialize the FacetGrid object
# pal = sns.cubehelix_palette(10, rot=-.25, light=.7)
# g = sns.FacetGrid(relevant, row=relevant.columns, hue=relevant.columns, aspect=15, height=.5, palette=pal)

# # Draw the densities in a few steps
# g.map(sns.kdeplot, "x", clip_on=False, shade=True, alpha=1, lw=1.5, bw=.2)
# g.map(sns.kdeplot, "x", clip_on=False, color="w", lw=2, bw=.2)
# g.map(plt.axhline, y=0, lw=2, clip_on=False)


# # Define and use a simple function to label the plot in axes coordinates
# def label(x, color, label):
#     ax = plt.gca()
#     ax.text(0, .2, label, fontweight="bold", color=color,
#             ha="left", va="center", transform=ax.transAxes)


# g.map(label, "x")

# # Set the subplots to overlap
# g.fig.subplots_adjust(hspace=-.25)

# # Remove axes details that don't play well with overlap
# g.set_titles("")
# g.set(yticks=[])
# g.despine(bottom=True, left=True)
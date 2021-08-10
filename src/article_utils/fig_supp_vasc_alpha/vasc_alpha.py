import pathlib

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib


matplotlib.rc('font', size=24)

fname = pathlib.Path('/data/neural_collision_detection/yoav/alpha_shapes_for_vasculature.csv')

data = pd.read_csv(fname, header=None, index_col=None, names=['x', 'y', 'z', 'alpha'])
ax = data.alpha.plot.hist(bins=100, color='C0')
sns.despine(ax=ax, offset=10)
ax.set_xlabel('Alpha Value')
ax.figure.tight_layout()
ax.figure.savefig('/data/neural_collision_detection/results/for_article/fig_supp_vasc_alpha/vasc_alpha.png', transparent=True, dpi=300)
ax.figure.savefig('/data/neural_collision_detection/results/for_article/fig_supp_vasc_alpha/vasc_alpha.pdf', transparent=True, dpi=300)
plt.show()

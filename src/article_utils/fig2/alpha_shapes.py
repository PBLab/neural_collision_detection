import numpy as np

import chart_studio.plotly as py
from plotly.graph_objs import *
from plotly.graph_objs.scatter3d import Marker as sMarker
from plotly.graph_objs.layout import Scene as lScene
from plotly import tools as tls

fname = "/data/neural_collision_detection/results/2020_02_14/normalized_agg_results_AP130312_s1c1_thresh_0.npz"
d = np.load(fname)["neuron_coords"]
x, y, z = d[:, 0], d[:, 1], d[:, 2]

points = Scatter3d(
    mode="markers", name="", x=x, y=y, z=z, marker=sMarker(size=2, color="#458B00")
)


simplexes = Mesh3d(
    alphahull=20.0,
    name="",
    x=x,
    y=y,
    z=z,
    color="#90EE90",  # set the color of simplexes in alpha shape
    opacity=0.25,
)


x_style = dict(
    zeroline=False,
    range=[x.min(), x.max()],
    tickvals=np.linspace(x.min(), x.max(), 5)[1:].round(1),
)
y_style = dict(
    zeroline=False,
    range=[y.min(), y.max()],
    tickvals=np.linspace(y.min(), y.max(), 4)[1:].round(1)
)
z_style = dict(
    zeroline=False, range=[z.min(), z.max()], tickvals=np.linspace(z.min(), z.max(), 5).round(1)
)


layout = Layout(
    title="Alpha shape of a set of 3D points. Alpha=0.1",
    width=500,
    height=500,
    scene=lScene(xaxis=x_style, yaxis=y_style, zaxis=z_style),
)


# fig = Figure(data=[points, simplexes], layout=layout)

# fig.show(renderer='svg')
# fig.show()

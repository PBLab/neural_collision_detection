import pathlib
import numpy as np
import vispy.color
import napari

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    CollisionsDistNaive,
)


def transform_coll_to_color(df, cmap='viridis', transparency=1.):
    """Use an existing DF with the collision counts and locations
    and find the value of the collision color for each of the
    rows in that DF.
    """
    # df["coll_stretch"] = df["coll"] / df["coll"].max()
    df["coll_stretch"] = df["coll"] / df["coll"].max()
    df = df.assign(r=np.nan, g=np.nan, b=np.nan, a=np.nan)
    cmap = vispy.color.get_colormap(cmap)
    df.loc[:, ["r", "g", "b", "a"]] = cmap[df["coll_stretch"].to_numpy()].rgba
    df.loc[:, "a"] *= transparency
    return df


if __name__ == "__main__":
    fname = pathlib.Path(
        "/data/neural_collision_detection/results/2019_2_10/graph_AP130312_s1c1_with_collisions.gml"
    )
    neuron_name = "AP130312_s1c1"
    g = CollisionsDistNaive.from_graph(fname, neuron_name)
    g.run()
    nc_ax = g.parsed_axon.loc[:, ["coll", "x", "y", "z"]]
    nc_dend = g.parsed_dend.loc[:, ["coll", "x", "y", "z"]]
    alpha_factor = 0.5
    scale_factor = 7
    nc_ax = transform_coll_to_color(nc_ax, "greens", alpha_factor)
    nc_dend = transform_coll_to_color(nc_dend, "orange", alpha_factor)

    with napari.gui_qt():
        v = napari.view_points(nc_dend.loc[:, "x":"z"].to_numpy(), size=nc_dend.loc[:, "coll_stretch"] * scale_factor, edge_width=0, face_color=nc_dend.loc[:, "r":"a"].to_numpy())
        v.add_points(nc_ax.loc[:, "x":"z"].to_numpy(), size=nc_ax.loc[:, "coll_stretch"] * scale_factor, edge_width=0, face_color=nc_ax.loc[:, "r":"a"].to_numpy())
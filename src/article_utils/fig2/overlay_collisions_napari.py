import pathlib
import numpy as np
import vispy.color
import napari

from ncd_post_process.create_neuron_id.collisions_vs_dist_naive import (
    CollisionsDistNaive,
)


def transform_coll_to_color(df, cmap="viridis", transparency=1.0):
    """Use an existing DF with the collision counts and locations
    and find the value of the collision color for each of the
    rows in that DF.
    """
    df["coll_stretch"] = df["coll"] / df["coll"].max()
    df = df.assign(r=np.nan, g=np.nan, b=np.nan, a=np.nan)
    cmap = vispy.color.get_colormap(cmap)
    df.loc[:, ["r", "g", "b", "a"]] = cmap[df["coll_stretch"].to_numpy()].rgba
    df.loc[:, "a"] *= transparency
    return df


def find_top_collision_sites(g: CollisionsDistNaive, quantile=0.9):
    """Returns the locations that had the best collision chance.
    """
    axq = g.parsed_axon["coll"].quantile(quantile)
    dendq = g.parsed_dend["coll"].quantile(quantile)
    allq = g.all_colls["coll"].quantile(quantile)
    ax = g.parsed_axon["coll"] >= axq
    dend = g.parsed_dend["coll"] >= dendq
    all_ = g.all_colls["coll"] >= allq
    return ax.to_numpy(), dend.to_numpy(), all_.to_numpy()


def show_collisions_with_napari(g: CollisionsDistNaive, viewer: napari.Viewer):

    colors = ['green', 'orange', 'red', 'yellow', 'purple']
    points = g.all_colls.set_index('type')
    points["color"] = ""
    for color, type_ in zip(colors, points.index.categories):
        points.loc[type_, "color"] = color
        viewer.add_points(points.loc[type_, "x":"z"], size=2, edge_width=0, face_color=color, name=f"{g.neuron_name}_{type_}")

    # colls = points.loc[:, "x":"z"].to_numpy()
    # colls_colors = points.loc[:, "color"].to_numpy().tolist()
    # viewer.add_points(colls, size=2, edge_width=0, face_color=colls_colors,)


if __name__ == "__main__":
    results_folder = pathlib.Path("/data/neural_collision_detection/results/2020_02_14")
    neuron_names = [
        "AP120410_s1c1",
        "AP120410_s3c1",
        'AP120412_s3c2',
        "AP120416_s3c1",
        "AP120419_s1c1",
        "AP120420_s1c1",
        "AP120420_s2c1",
        "AP120510_s1c1",
        "AP120524_s2c1",
        "AP120614_s1c2",
        "AP130312_s1c1",
    ]
    alpha_factor = 0.5
    scale_factor = 7

    with napari.gui_qt():
        viewer = napari.Viewer(ndisplay=3)
        for neuron_name in neuron_names:
            print(neuron_name)
            fname = results_folder / f"graph_{neuron_name}_with_collisions.gml"
            g = CollisionsDistNaive.from_graph(fname, neuron_name)
            g.run()
            show_collisions_with_napari(g, viewer)
            # nc_ax = g.parsed_axon.loc[:, ["coll", "x", "y", "z"]]
            # nc_dend = g.parsed_dend.loc[:, ["coll", "x", "y", "z"]]
            # nc_ax = transform_coll_to_color(nc_ax, "greens", alpha_factor)
            # nc_dend = transform_coll_to_color(nc_dend, "orange", alpha_factor)
            # top_ax, top_dend, top_all = find_top_collision_sites(g)
            # viewer.add_points(
            #     nc_dend.loc[:, "x":"z"].to_numpy(),
            #     size=nc_dend.loc[:, "coll_stretch"] * scale_factor,
            #     edge_width=0,
            #     face_color=nc_dend.loc[:, "r":"a"].to_numpy(),
            #     name=f"{neuron_name}_dend",
            # )
            # viewer.add_points(
            #     nc_ax.loc[:, "x":"z"].to_numpy(),
            #     size=nc_ax.loc[:, "coll_stretch"] * scale_factor,
            #     edge_width=0,
            #     face_color=nc_ax.loc[:, "r":"a"].to_numpy(),
            #     name=f"{neuron_name}_ax",
            # )
            # viewer.add_points(
            #     nc_ax.loc[top_ax, "x":"z"],
            #     size=4,
            #     edge_width=0,
            #     face_color='white',
            #     name=f"{neuron_name}_top_ax",
            # )
            # viewer.add_points(
            #     nc_dend.loc[top_dend, "x":"z"],
            #     size=4,
            #     edge_width=0,
            #     face_color='gray',
            #     name=f"{neuron_name}_top_dend",
            # )
            # viewer.add_points(
            #     g.all_colls.loc[:, ["x", "y", "z"]],
            #     size=4,
            #     face_color='magenta',
            #     name=f"{neuron_name}_top_all"
            # )

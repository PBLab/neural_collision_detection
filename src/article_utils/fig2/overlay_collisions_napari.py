import pathlib
import numpy as np
import vispy.color
import napari
import pandas as pd

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


def show_collisions_with_napari(
    points: pd.DataFrame, viewer: napari.Viewer, neuron_name: str, size=None
):
    """Plot the collisions of the neuron with the given napari viewer.

    This function receives the points to be plotted, the viewer instance to be used
    and the name of the current neuron (to be used as the layer's label) and shows
    them all together. The given dataframe is assumed to have a 'type' categorical
    index which contains information on the type of neurite this collision is located
    on top of.

    Parameters
    ----------
    size : str, int, array (optional)
        Size of each point. If int - size in pixels. If None - defaults to 2.
        If str - should be a column name in `points`. If array - size of each
        point.
    """
    if size is None or isinstance(size, (int, np.ndarray)):
        points["size"] = size
    elif isinstance(size, str):
        points = points.rename({size: "size"}, axis=1)

    colors = ["green", "orange", "red", "yellow", "purple"]
    points["color"] = ""
    for color, type_ in zip(colors, points.index.categories):
        points.loc[type_, "color"] = color
        viewer.add_points(
            points.loc[type_, "x":"z"],
            size=points.loc[type_, "size"],
            edge_width=0.5,
            edge_color='black',
            face_color=color,
            name=f"{neuron_name}_{type_}",
        )

    # colls = points.loc[:, "x":"z"].to_numpy()
    # colls_colors = points.loc[:, "color"].to_numpy().tolist()
    # viewer.add_points(colls, size=2, edge_width=0, face_color=colls_colors,)


if __name__ == "__main__":
    results_folder = pathlib.Path("/data/neural_collision_detection/results/2020_07_29")
    neuron_names = [
        # "AP120410_s1c1",
        # "AP120410_s3c1",
        # "AP120412_s3c2",
        # "AP120416_s3c1",
        "AP120419_s1c1",
        # "AP120420_s1c1",
        # "AP120420_s2c1",
        # "AP120507_s3c1",
        # "AP120510_s1c1",
        # "AP120522_s3c1",
        # "AP120523_s2c1",
        "AP120524_s2c1",
        "AP120614_s1c2",
        "AP130110_s2c1",
        "AP130312_s1c1",
        "AP130606_s2c1",
        "AP131105_s1c1",
        # "MW120607_LH3",
    ]
    alpha_factor = 0.5
    scale_factor = 7

    with napari.gui_qt():
        viewer = napari.Viewer(ndisplay=3)
        for neuron_name in neuron_names:
            print(neuron_name)
            fname = results_folder / f"graph_{neuron_name}_with_collisions.gml"
            try:
                g = CollisionsDistNaive.from_graph(fname, neuron_name)
                g.run()
            except FileNotFoundError:
                continue
            points = g.all_colls.astype({'type': 'category'}).set_index("type")
            # show_collisions_with_napari(points, viewer, neuron_name, 'coll_normed')
            nc_ax = g.parsed_axon.loc[:, ["coll", "x", "y", "z"]]
            nc_dend = g.parsed_dend.loc[:, ["coll", "x", "y", "z"]]
            nc_ax = transform_coll_to_color(nc_ax, "greens", alpha_factor)
            nc_dend = transform_coll_to_color(nc_dend, "orange", alpha_factor)
            # top_ax, top_dend, top_all = find_top_collision_sites(g)
            viewer.add_points(
                nc_dend.loc[:, "x":"z"].to_numpy(),
                size=nc_dend.loc[:, "coll_stretch"] * scale_factor,
                edge_width=0.2,
                edge_color='black',
                face_color=nc_dend.loc[:, "r":"a"].to_numpy(),
                name=f"{neuron_name}_dend",
            )
            viewer.add_points(
                nc_ax.loc[:, "x":"z"].to_numpy(),
                size=nc_ax.loc[:, "coll_stretch"] * scale_factor,
                edge_width=0.2,
                edge_color='black',
                face_color=nc_ax.loc[:, "r":"a"].to_numpy(),
                name=f"{neuron_name}_ax",
            )
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

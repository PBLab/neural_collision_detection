""" Should only be run under Blender """
import sys
import pathlib
from itertools import product

import numpy as np
import bpy
sys.path.append(
    "/data/neural_collision_detection/src"
)
from mytools import *

from ncd_post_process.alpha_shapes.find_block_properties import load_neuronal_points, divide_neuron_into_blocks


OPS_LAYER = 0


def get_bottom_left_corner(mins: tuple, maxes: tuple) -> tuple:
    """Returns the bottom-left corner of a given cube"""
    pass


def draw_boxes(linspace_per_ax: list):
    """Iterates over the boxes limits and draws a cube for each"""
    bin_starts = product(*(ax[:-1] for ax in linspace_per_ax))
    bin_ends = product(*(ax[1:] for ax in linspace_per_ax))
    voxel_faces = [
            [0, 1, 3, 2],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 3, 7, 5],
            [3, 2, 6, 7],
            [2, 0, 4, 6],
        ]
    for coll_start, coll_end in zip(bin_starts, bin_ends):  
        voxel_verts = [
                [*coll_start],
                [coll_end[0], *coll_start[1:]],
                [coll_start[0], coll_end[1], coll_start[2]],
                [*coll_end[:2], coll_start[2]],
                [*coll_start[:2], coll_end[2]],
                [coll_end[0], coll_start[1], coll_end[2]],
                [coll_start[0], *coll_end[1:]],
                [*coll_end],
            ]
        name = "bounding box"
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.objects.link(obj)
        # obj.select_set('SELECT')
        mesh.from_pydata(voxel_verts, [], voxel_faces)
        mesh.update(calc_edges=True)
        # apply material
        mat = bpy.data.materials.new(name + "_Mat")
        mat.diffuse_color = [1.0, 0.0, 0.0]
        mat.diffuse_shader = "LAMBERT"
        mat.diffuse_intensity = 1.0
        mat.specular_color = [0.0, 0.0, 0.0]
        mat.specular_shader = "COOKTORR"
        mat.specular_intensity = 1.0
        mat.alpha = 0.2
        mat.ambient = 0.2
        mat.transparency_method = 'Z_TRANSPARENCY'
        obj.data.materials.append(mat)

        # set layers
        layers = [False] * 20
        layers[(bpy.context.scene["MyDrawTools_BaseLayer"] + OPS_LAYER) % 20] = True
        obj.layers = layers


if __name__ == '__main__':
    path = pathlib.Path(
        "/data/neural_collision_detection/results/2020_02_14/graph_AP120410_s1c1_with_collisions.gml"
    ).resolve()
    points = load_neuronal_points(path, "AP120410")
    indices, bins = divide_neuron_into_blocks(points.loc[:, "x":"z"], (10, 19, 6))
    draw_boxes(bins)

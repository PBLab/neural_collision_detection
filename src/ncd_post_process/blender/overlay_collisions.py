"""
This script, when run under Blender, shows the distribution
of collision on a given neuron.

This is done by first rendering the neuron in Blender using
standard py3DN procedure, and then running this code
as a script, whilst giving it the proper inputs - i.e.
the correct neuron name and its collisions data.

The result is shown by overlaying cubes on top of the neuron,
the color of which is indicative of the number of collisions
that were registered in that bin.
"""
import pathlib
from collections import namedtuple

import numpy as np
import bpy

import DrawingXtras
from mytools import *


class OverlayCollisions:
    """
    Shows a 3D histogram of collisions in Blender
    on top of a rendered object. Please create it using one
    of the "from_" methods, and not directly, and then
    call "run()".
    """

    def __init__(self, collisions, binsize=(5, 5, 5)):
        self.collisions = collisions
        self.binsize = binsize

    def run(self):
        """
        Main pipeline. Any needed pre-processing steps happen in
        the classmethods that instatiate this object.
        """
        hist, edges = self._gen_bins(self.binsize)
        nonzero_hist, bin_starts, bin_ends = self._filter_relevant_bins(hist, edges)
        self._create_verts_faces_and_draw(
            nonzero_hist, bin_starts, bin_ends, OPS_LAYER=4
        )

    @classmethod
    def from_vasc_density(cls, fname, binsize=(5, 5, 5)):
        """
        Shows the vascular density of the
        """
    @classmethod
    def from_top_collisions(cls, fname, binsize=(5, 5, 5)):
        """
        Overlay the collisions with the top percentage
        of collisions input. The input is an Nx3 array, each
        row being a coordinate on top of the neuron that collided
        with the vasculature.
        """
        fname = pathlib.Path(fname)
        assert fname.exists()
        collisions = np.load(fname)
        return cls(collisions, binsize)

    @classmethod
    def from_all_collisions(cls, fname, binsize=(5, 5, 5), downsample_factor=1000):
        """
        Overlay collisions with the input being an Nx3 array, each row
        being a coordinate on top of the neuron that collided with the
        vasculature.
        """
        fname = pathlib.Path(fname)
        assert fname.exists()
        collisions = np.load(fname)["neuron_coords"][::downsample_factor, :]
        collisions = cls._filter_nans(collisions)
        return cls(collisions, binsize)

    @staticmethod
    def _filter_nans(collisions):
        """Remove all-nan collisions from the array."""
        allnan_rows = np.where(np.all(np.isnan(collisions), axis=1))[0]
        collisions = np.delete(collisions, allnan_rows, axis=0)
        return collisions
    
    def _gen_bins(self, l: tuple):
        """ Histograms the collisions into l-sized bins """
        print(np.isnan(self.collisions).sum())
        max_x, min_x = np.max(self.collisions[:, 0]), np.min(self.collisions[:, 0])
        max_y, min_y = np.max(self.collisions[:, 1]), np.min(self.collisions[:, 1])
        max_z, min_z = np.max(self.collisions[:, 2]), np.min(self.collisions[:, 2])
        bins_x = int(np.ceil(max_x - min_x / l[0]))
        bins_y = int(np.ceil(max_y - min_y / l[1]))
        bins_z = int(np.ceil(max_z - min_z / l[2]))
        hist, edges = np.histogramdd(self.collisions, bins=(bins_x, bins_y, bins_z))
        return hist, edges

    def _filter_relevant_bins(self, hist, edges):
        """
        After generating the histogram of collisions, filters out only
        the bins in which a collisions occurred. It then generates two
        arrays which contain the start and end of the bins containing the
        collisions in microns.
        """
        relevant_coords = np.where(
            hist > 0
        )  # each row is a dimension, each column a coordinate
        num_dims = 3
        num_ones = len(relevant_coords[0])
        bin_starts = np.zeros((num_ones, num_dims))
        bin_ends = np.zeros_like(bin_starts)
        assert len(edges) == len(relevant_coords)
        for coor_idx, (coor, edge) in enumerate(zip(relevant_coords, edges)):
            bin_starts[:, coor_idx] = edge[coor]
            bin_ends[:, coor_idx] = edge[coor + 1]

        return hist[relevant_coords], bin_starts, bin_ends

    def _create_verts_faces_and_draw(self, hist, bin_starts, bin_ends, OPS_LAYER=4):
        """
        After generating a 3D histogram of collisions on top of the neuron,
        create a new mesh in Blender which shows the number of collisions in
        that bin in space by modifying the color brightness of that spot - the
        brighter the generated mesh is, the more collisions occurred.

        Based on a function from py3DN.
        """
        norm = 1.0 / (hist.max() * 0.5)
        for val, coll_start, coll_end in zip(hist, bin_starts, bin_ends):
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
            voxel_faces = [
                [0, 1, 3, 2],
                [4, 5, 7, 6],
                [0, 1, 5, 4],
                [1, 3, 7, 5],
                [3, 2, 6, 7],
                [2, 0, 4, 6],
            ]
            # Draw
            # ----------------------------------------------------
            name = "collisions"
            mesh = bpy.data.meshes.new(name + "_Mesh")
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            # obj.select_set('SELECT')
            mesh.from_pydata(voxel_verts, [], voxel_faces)
            mesh.validate(verbose=True)
            mesh.update(calc_edges=True)
            # apply material
            mat = bpy.data.materials.new(name + "_Mat")
            mat.diffuse_color = [val * norm, 0.0, 0.0, 1.0]
            mat.specular_color = [0.0, 0.0, 0.0]
            # mat.transparency_method = 'Z_TRANSPARENCY'
            obj.data.materials.append(mat)


if __name__ == "__main__":
    # Should only be run under Blender
    l = (5, 5, 5)  # in um
    fname = r"/data/neural_collision_detection/results/for_article/fig1/normalized_artificial_neuron_results_agg_thresh_0.npz"
    downsample_factor = 1
    OverlayCollisions.from_all_collisions(fname=fname, binsize=l).run()

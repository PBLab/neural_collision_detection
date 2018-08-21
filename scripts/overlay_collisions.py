import numpy as np
import DrawingXtras
from mytools import *
from collections import namedtuple
import bpy

Coor = namedtuple('Coor', ('x', 'y', 'z'))

def get_border_box(neuron, l):
    """ 
    Returns three 3D objects: 
    bins: the number of bins in each dimension for a given neuron,
    normalized to a l.x-by-l.y-by-l.z box in um. 
    maxp: Maximal coordinate of the neuron in all three dimensions.
    minp: Minimal coordinate of the neuron in all three dimensions.
    Assumes that at least a single neuron was already loaded, and that 
    mytools was imported. 
    Taken directly from Py3DN with very minor changes by Hagai Har-Gil.
    """
    
    # to make things more readable
    X = 0
    Y = 1
    Z = 2

    # Find out how many coordinates the neuron contains
    num_of_dims = 3
    num_of_points = 0
    for tree in neuron.tree:
        num_of_points += len(tree.rawpoint)
    neuron_coords = np.zeros((num_of_points, num_of_dims))

    row = 0
    for tree in neuron.tree:
        for point in tree.rawpoint:
            neuron_coords[row, :] = point.P
            row += 1
    

    min_point = neuron_coords.min(axis=0)
    max_point = neuron_coords.max(axis=0)
    
    bins_x = int((max_point[X] - min_point[X]) / l.x) + 2
    bins_y = int((max_point[Y] - min_point[Y]) / l.y) + 2
    bins_z = int((max_point[Z] - min_point[Z]) / l.z) + 2
    
    bins = Coor(bins_x, bins_y, bins_z)
    maxp = Coor(max_point[X], max_point[Y], max_point[Z])
    minp = Coor(min_point[X], min_point[Y], min_point[Z])
    
    return bins, maxp, minp


def draw_collisions(cols, l, bins, maxp, minp, OPS_LAYER=0):
    """ 
    Assuming we have a loaded neuron (and mytools imported) with its corresponsing
    collisions array computed by NCL (neural collision detector), this function renders 
    the collision points on top of the loaded neuron.
    cols: Collision array from the NCD pipeline.
    l: Coor namedtuple of the size of each voxel in um.
    bins: Coor namedtuple of the bin size in each dimension.
    maxp: Coor namedtuple of the maximal coordinate in which the neuron is located.
    minp: Coor namedtuple of the minimal coordinate in which the neuron is located.
    OPS_LAYER (0): The default layer to place the collision information.
    Taken directly from Py3DN, with very minor changes by Hagai Har-Gil. 
    """
    max_collisions = np.max(cols)
    print("The maximum number of collisions in a bin is {}".format(max_collisions))
    norm = 1./np.max(max_collisions)

    
    it = np.nditer(cols, flags=['multi_index'])
    while not it.finished:
        if it[0] <= 0:
            it.iternext()
            continue
    
        cur_min = Coor(minp.x + it.multi_index[0] * l.x,
                       minp.y + it.multi_index[1] * l.y,
                       minp.z + it.multi_index[2] * l.z)
        cur_max = Coor(cur_min.x + l.x,
                       cur_min.y + l.y,
                       cur_min.z + l.z)
        voxel_verts = [[cur_min.x, cur_min.y, cur_min.z], [cur_max.x, cur_min.y, cur_min.z],
                        [cur_min.x, cur_max.y, cur_min.z], [cur_max.x, cur_max.y, cur_min.z],
                        [cur_min.x, cur_min.y, cur_max.z], [cur_max.x, cur_min.y, cur_max.z],
                        [cur_min.x, cur_max.y, cur_max.z], [cur_max.x, cur_max.y, cur_max.z]]
        voxel_faces = [[0,1,3,2], [4,5,7,6], [0,1,5,4], [1,3,7,5], [3,2,6,7], [2,0,4,6]]
                
        # Draw
        # ----------------------------------------------------
        name = 'collisions'
        mesh = bpy.data.meshes.new( name + '_Mesh' )
        obj  = bpy.data.objects.new( name, mesh )
        bpy.context.scene.objects.link( obj )
        mesh.from_pydata( voxel_verts, [], voxel_faces)
        mesh.update( calc_edges = True )
        # apply material
        mat = bpy.data.materials.new( name + '_Mat')
        mat.diffuse_color = [it[0] * norm, 0.0, 0.0]
        mat.diffuse_shader = 'LAMBERT'
        mat.diffuse_intensity = 1.0
        mat.specular_color = [0.0, 0.0, 0.0]
        mat.specular_shader = 'COOKTORR'
        mat.specular_intensity = 1.0
        mat.alpha = it[0] * norm * 0.5
        mat.ambient = 1.0
        #mat.transparency_method = 'Z_TRANSPARENCY'
        obj.data.materials.append(mat)

        # set layers
        layers = [False]*20
        layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
        obj.layers = layers
        it.iternext()


if __name__ == '__main__':
    l = Coor(5, 5, 5)  # in um
    bins, maxp, minp = get_border_box(neuron[0], l)
    print(bins)
    
    fname = r'C:\Py3DN\SampleCells\collisions_array_AP120420_s1c1.npz'
    collisions = np.load(fname)['arr_0']
    print(collisions.shape)
    assert collisions.shape == (bins.x, bins.y, bins.z)
    draw_collisions(collisions, l, bins, maxp, minp)

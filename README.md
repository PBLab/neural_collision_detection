# Neural Collision Detection Documentation

1	Background
==============
### 1.1	The problem

Given vascular data and a neuron in a specific location, we want to efficiently
calculate the optimal rotation of the neuron, regarding collision points between
the neuron and the surronding blood vessels.

### 1.2	The solution - ncd Program

We introduce a program named ncd (which stands for Neural Collision Detection).
Given vascular data and neural data, the program computes the number of collisions
between the two, for all possible rotation in a specific location.

	
2	Preparing the data for ncd:
===============================
The data is located in Yoav's Stromboli user, but also in PBLab's QNAP, in the folder `simulated_morph_data`.

2.1	Preliminary data is received as a polygon mesh, in matlab

2.2	The mesh is stored in CSV format, with the following matlab commands:

For neurons, to move them back to (0,0,0):

	dlmwrite('vertices.csv', bsxfun(@minus, vertices, offsetXYZ), 'precision', 7)
	dlmwrite('faces.csv', faces, 'precision', 7)

For vascular data:

	dlmwrite('vertices.csv', vertices, 'precision', 7)
	dlmwrite('faces.csv', faces, 'precision', 7)

2.3	The mesh is translated to the more commonly used .obj format:

	python csv_to_obj.py <vertices.csv> <faces.csv> <output.obj>

2.4	The mesh is simplified, with the external program Fast-Quadric-Mesh-Simplification

	simplify <input obj> <output obj> <ratio>
	
Recommended ratio for neurons: 0.1

Recommended ratio for vascular data: 0.01 (This may be improved in the future)

2.5	The output files can then be passed to ncd

3	Usage of ncd
================
The command line is as follows:

    ./ncd -V <vascular_path> -N <neuron_path> -f <output_path>
         [-t num_of_threads] [-c max_num_of_collisions] [-m main_axis]
         -x <x_coordinate> -y <y_coordinate> -z <z_coordinate>

Recommended params:

	vascular_path, neuron_path - paths to .obj files, from stage 2
	output_path - file name of the results file
	num_of_threads - 36 on stromboli server
	max_num_of_collisions - 30000, but may change according to results
	main_axis - the neuron rotates around this axis 360 degrees. Default - z
	x,y,z coordinates - the  location of the center of the neuron

4	Characteristics of ncd
==========================

4.1	Collisions computation

The collision computation itself is done using an open source library called
fcl (Flexible Collision Library). 

4.2	Running time

The running time is affected by several factors:

- The complexity of the original meshes 
- The simplification factor
- The server running ncd
- The amount of collisions requested
  
On stromboli server, with the recommended simplification, the running is
between 10 minutes and 15 minutes. Take into account that it may vary
if the mentioned factors are changed.

4.3	Output file

The outputfile contains the number of collisions, per rotation.
For rotation `(x0,y0,z0)`, it means a rotation of `x0` degrees around x-axis,
then `y0` degrees around y-axis and then `z0` degrees around z-axis


5	Future work
===============

5.1	Non-rigid body

5.2 Improve mesh

This file explains the pipeline, and the usage of each script file in this directory.


Main scripts:
	aggregator.py
		Usage: aggregator.py <vascular data> <neuron data> <location> <rotation> <results file>

	run_aggregator.py
		Usage: run_aggregator.py <base dir> <out dir>

	gather_agg_results.py
		Usage: gather_agg_results.py <input directory> <output file>

	neuron_parser.py
		Usage: neuron_parser.py <input file> <output directory>

	parser.py
		No usage, shouldn't be run as a standalone tool.


Utils:
	create_cube.py
		Usage: create_cube.py <output file> <radius> <location>
		Creates an .obj file, with a single cube of given radius (half edge size) and location.
	extend.py
		 extend.py <input filename> <output filename>
		 Extends Centers.csv to have more centers, so we have more data. Used only for R&D.
	collisions_to_cubes.py
		Usage: collisions_to_cubes.py <input file> <output dir>
		Receives a list of collisions (locations), and creates multiple .obj files, each represent a collision as a cube.
		Used to visualize collisions on a neuorn/blood vessel.
	find_enclosing_box.py
		Usage: find_enclosing_box.py <object>
		Gets an object (.csv/.obj file), and outputs its bounding box. Used for debugging, and as a utility by other scripts.
	verify_zeros.py
		Usage: verify_zeros.py <base dir>
		Runs ncd in verify mode on each position with zero collisions, for debugging purposes.

Other:
	plotter.py
		Plots a general 2D array, using matplotlib. Not really needed right now.
	plotter_3d.py
		Just an example from the web. Not really needed right now.

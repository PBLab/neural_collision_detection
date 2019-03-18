#!/usr/bin/python

import os, sys, re
import multiprocessing
import pathlib

import numpy as np
import pandas as pd

from aggregator import aggregate, get_vascular


def get_ncd_results(ncd_output_file, max_collisions):
	results = []
	with open(ncd_output_file, "r") as f:
		for l in f:
			splitted = l.split(",")
			if len(splitted) < 7:
				continue
			if int(splitted[7]) > max_collisions:
				continue
			results.append(l)

	return results


def process_main(results, output_fname, threshold_distance, vascular):
	for res in results:
		splitted = res.split(",")

		neuron_name = splitted[0].replace(".obj", "_balls.csv")
		location = [int(splitted[1]), int(splitted[2]), int(splitted[3])]
		rotation = [int(splitted[4]), int(splitted[5]), int(splitted[6])]

		parent_folder = pathlib.Path(__file__).resolve().parents[2]
		neuron_fname = str(parent_folder / "neurons" / neuron_name)
		vascular_fname = str(parent_folder / "vascular" / "vascular_balls.csv")

		aggregate(vascular_fname, neuron_fname, location, rotation, output_fname, threshold_distance, vascular)


def process_main_from_mem(results: pd.DataFrame, output_fname, threshold_distance, vascular):
    """
    Each process spawned from "main_from_mem" runs this function on all of the collision
    data it was assigned to.
    """
    location = results.loc[:, 'x':'z'].to_numpy().astype(np.int64)
    rotation = results.loc[:, 'tip':'yaw'].to_numpy().astype(np.int64)
    neuron_name = results['neuron_name'].iloc[0].replace('.obj', '_balls.csv')
    parent_folder = pathlib.Path(__file__).resolve().parents[2]
    neuron_fname = str(parent_folder / "neurons" / neuron_name)
    vascular_fname = str(parent_folder / "vascular" / "vascular_balls.csv")
    for loc, rot in zip(location, rotation):
        aggregate(vascular_fname, neuron_fname, loc, rot, output_fname, threshold_distance, vascular)


def main_from_mem(ncd_results, threshold_distance, output_fname, vascular_fname):
    """
    Aggregate the NCD result files into a parsable DB while filtering it
    based on the threshold distance of the collisions.
    Receives the NCD data as an in-memory object, rather than
    a filename.
    """
    process_count = 20
    results_per_process = 1.0 * len(ncd_results) / process_count
    processes = []
    last_idx = 0
    vascular = get_vascular(vascular_fname)
    for i in range(process_count):
    	next_idx = int(results_per_process * (i + 1))
    	if i == process_count - 1:
    		next_idx = len(ncd_results)
    	params = (ncd_results.iloc[last_idx:next_idx, :], output_fname, threshold_distance, vascular)
    	p = multiprocessing.Process(target=process_main_from_mem, args=params)
    	processes.append(p)
    	p.start()
    	last_idx = next_idx
    for i in range(process_count):
    	processes[i].join()


def main(argv):
	if len(argv) < 4:
		print("Usage: %s <ncd output file> <max collisions> <threshold distance> <output file>" % argv[0])
		return 1

	ncd_output_file = argv[1]
	max_collisions = int(argv[2])
	threshold_distance = int(argv[3])
	output_fname = argv[4]

	ncd_results = get_ncd_results(ncd_output_file, max_collisions)
	print("Running over {0} results".format(len(ncd_results)))

	process_count = 20
	results_per_process = 1.0 * len(ncd_results) / process_count
	processes = []
	last_idx = 0
	parent_folder = pathlib.Path(__file__).resolve().parents[2]
	vascular_fname = str(parent_folder / "vascular/vascular_balls.csv")
	vascular = get_vascular(vascular_fname)

	for i in range(process_count):
		next_idx = int(results_per_process * (i + 1))
		if i == process_count - 1:
			next_idx = len(ncd_results)

		params = (ncd_results[last_idx : next_idx], output_fname, threshold_distance, vascular)
		print(len(params[0]))

		p = multiprocessing.Process(target=process_main, args = params)
		processes.append(p)
		p.start()
		last_idx = next_idx

	for i in range(process_count):
		processes[i].join()

if __name__ == "__main__":
	sys.exit(main(sys.argv))

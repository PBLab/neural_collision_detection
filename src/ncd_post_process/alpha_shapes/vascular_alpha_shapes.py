#!/opt/miniconda3/bin/python
"""
Main script to calculate the alpha values for the geometrical
shape of a vascular.
"""
import pathlib
import sys
import multiprocessing

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


sys.path.append(
	"../../cgal-python-bindings/src/alpha3_bindings/delaunay_fast_location_release"
)
from tri3_epic import *

sys.path.pop(-1)


def generate_alphashape_from_vascular(vascular_name):
	"""For a given vascular name, iterate over its points and return
	an Alpha Shape object.
	"""
	all_points = []
	points = pd.read_csv(vascular_name, header=None)
	for _, point in points.iterrows():
		all_points.append(Point_3(point.iloc[0], point.iloc[1], point.iloc[2]))
	return Alpha_shape_3(all_points), all_points


def get_all_alpha_values(shp: Alpha_shape_3):
	"""Returns an array of all needed alpha shapes"""
	num = range(shp.number_of_alphas())
	alphas = [shp.get_nth_alpha(idx) for idx in num]
	alphas.pop(0)  # first val is always 0
	return alphas


def classify_points(shp: Alpha_shape_3, points: list, cls_dict: dict) -> np.ndarray:
	"""Iterates over the points of the alpha shape and classifies them,
	returning a dict with their values."""
	classified = np.empty(len(points), dtype=np.int8)
	for idx, point in enumerate(points):
		classified[idx] = cls_dict[str(shp.classify(point))]
	return classified


def sample_alphas(alphas: np.ndarray, factor=10) -> np.ndarray:
	len_ = len(alphas)
	alphas = np.asarray(alphas)
	return alphas[np.linspace(0, len_ - 1, len_ // factor, dtype=np.uint32)]


def process_single_shape(vascular_path):
	"""General alpha shape processing pipe"""
	alpha_shape, points = generate_alphashape_from_vascular(vascular_path)
	#output_folder = pathlib.Path("/data/neural_collision_detection/results/for_article/fig2")
	output_folder = "~/tmp" # TODO: change
	alphas = get_all_alpha_values(alpha_shape)
	print(
		f"Found {len(alphas)} alphas for vascular which has {len(points)} points."
	)
	alphas = sample_alphas(alphas)
	cls_dict = {
		"INTERIOR": np.int8(0),
		"EXTERIOR": np.int8(1),
		"REGULAR": np.int8(2),
		"SINGULAR": np.int8(3),
	}
	all_classifications = []
	for alpha in alphas:
		alpha_shape.set_alpha(alpha)
		classified = classify_points(alpha_shape, points, cls_dict)
		all_classifications.append(classified)
	all_classifications = pd.DataFrame(np.vstack(all_classifications).T, columns=alphas)
	all_classifications.attrs = {"vascular_name": "main_vascular"}
	all_classifications.to_csv(output_folder + "/main_vascular" + "_alpha_distrib.csv") # TODO: Change


def find_first_interior_alpha_shape_value(alphas: pd.DataFrame) -> np.ndarray:
	"""Finds the smallest alpha value that interiorized each point.

	When calculating alpha shapes, each point on the vascular is continuously
	checked for whether it's inside, on the edge, or outside the shape. The functions'
	goal is to detect the "transition" of each point from being on the outside of
	the shape (values of > 0) to being inside (value == 0).

	Parameters
	----------
	alphas : pd.DataFrame
		Neural points are on the rows and alpha shape values are the columns

	Returns
	-------
	np.ndarray
		The alpha value for each neural point. NaN if it's never found inside
	"""
	interior_alphas = np.where(alphas == 0)
	first_zeros = pd.DataFrame({"x": interior_alphas[0], "y": interior_alphas[1]})
	first_alpha = first_zeros.groupby("x").min()
	all_rows = np.full((alphas.shape[0],), np.nan)
	all_rows[first_alpha.index] = alphas.columns[first_alpha["y"]]
	return all_rows


if __name__ == "__main__":
	vascular_path = "/data/neural_collision_detection/data/vascular/from_yoav_050920/vascular_balls_final.csv"
	#vascular_path = "/data/neural_collision_detection/data/neurons/AP120510_s1c1_balls_yz_flipped.csv" # TODO: Change
	#vascular_path = "~/tmp/test.csv" # TODO: Change
	print ("Start")
	process_single_shape(vascular_path)

#!/usr/bin/python

from utils import Utils
import argparse
import time
import numpy
from triangulation import Triangulation


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("vertices")
    parser.add_argument("faces")
    parser.add_argument("output")
    parser.add_argument(
        "--expand", help="Ratio to expand neuron. For example: 1.15,1.15,1.40"
    )
    return parser


def main_commandline():
    parser = create_parser()
    args = parser.parse_args()
    x_expand, y_expand, z_expand = 1, 1, 1
    if args.expand is not None:
        x_expand, y_expand, z_expand = [float(x) for x in args.expand.split(",")]

    output_fname = args.output

    tr = Triangulation(args.faces, args.vertices)
    # tr.print_stats()

    creator = tr.get_obj_creator()
    creator.create_obj_file(output_fname, x_expand, y_expand, z_expand)
    print("\tDone!")


def main_lib(faces, vertices, output_fname, x_expand=1, y_expand=1, z_expand=1):
    """ Call the CSV to OBJ converter from a different functions,
    usually the batch converter """
    tr = Triangulation(faces, vertices)
    creator = tr.get_obj_creator()
    creator.create_obj_file(output_fname, x_expand, y_expand, z_expand)


if __name__ == "__main__":
    start_time = time.time()
    main_commandline()
    end_time = time.time()
    runtime = end_time - start_time
    print("\n-------------------------")
    print("Runtime: %f seconds" % runtime)

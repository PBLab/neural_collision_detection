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
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    output_fname = args.output

    tr = Triangulation(args.faces, args.vertices)
    #tr.print_stats()

    creator = tr.get_obj_creator()
    creator.create_obj_file(output_fname)

    print "\tDone!"


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    runtime = end_time - start_time
    print "\n-------------------------"
    print "Runtime: %f seconds" % runtime

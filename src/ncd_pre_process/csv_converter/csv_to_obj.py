import pathlib
import multiprocessing as mp

import argparse
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


def batch_csv_to_obj(foldername, globstr='faces*flipped.csv'):
    """ Parse the folder in search of faces and vertices """
    all_faces = foldername.rglob(globstr)
    args = []
    for face in all_faces:
        fname_face = str(face.name)[6:-4]  # removes "faces_" and ".csv"
        try:
            fname_vert = next(face.parent.glob('vert*' + fname_face + '.csv'))
        except StopIteration:
            print(f"file {fname_face} doesn't have a vertices counterpart.")
            continue
        obj_fname = face.parent / (fname_face + '.obj')
        args.append((str(face), str(fname_vert), str(obj_fname)))

    with mp.Pool() as pool:
        pool.starmap(main_lib, args)


if __name__ == "__main__":
    batch_csv_to_obj(pathlib.Path('/data/neural_collision_detection/src/convert_obj_matlab'))

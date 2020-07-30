import pathlib

from csv_converter import csv_to_obj


def find_csv(foldername):
    """ Parse the folder in search of faces and vertices """
    all_faces = foldername.rglob('faces*flipped.csv')

    for face in all_faces:
        fname_face = str(face.name)[6:-4]  # removes "faces_" and ".csv"
        try:
            fname_vert = next(face.parent.glob('vert*' + fname_face + '.csv'))
        except StopIteration:
            print(f"file {fname_face} doesn't have a vertices counterpart.")
            continue

        obj_fname = face.parent / (fname_face + '.obj')
        csv_to_obj.main_lib(str(face), str(fname_vert), str(obj_fname))


if __name__ == '__main__':
    find_csv(pathlib.Path('/data/neural_collision_detection/src/convert_obj_matlab'))


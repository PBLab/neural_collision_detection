import contextlib
import pathlib
import sys


@contextlib.contextmanager
def add_to_path(folder: pathlib.Path):
    """Adds given folder to the path, and pops it out when it's not needed anymore."""
    sys.path.append(str(folder))
    yield
    sys.path.pop(-1)


def generate_alpha_shape(foldername):
    """This is taken from the delaunay fast location script"""
    with add_to_path(foldername):
        from tri3_epic import *

    p1 = Point_3(1, 0, 0)
    p2 = Point_3(0, 1, 0)
    p3 = Point_3(0, 0, 1)
    alphaShape  = Alpha_shape_3([p1, p2, p3])
    # alphaShape.make_alpha_shape([p1, p2, p3])

    print("Alpha shape computed in REGULARIZED mode by default")
    # Find alpha solid
    alphaSolid = alphaShape.find_alpha_solid()
    print("Smallest alpha value to get a solid through data points is ", alphaSolid)
    # find optimal alpha value
    optHandle = alphaShape.find_optimal_alpha(1);
    print(optHandle)
    # optIter = optHandle.__iter__();
    optAlpha = next(optHandle)
    print("Optimal alpha value to get one connected component is ", optAlpha)
    alphaShape.set_alpha(optAlpha);
    num = alphaShape.number_of_solid_components()
    print("# solid components: ", num)


if __name__ == "__main__":
    foldername = '/data/MatlabCode/PBLabToolkit/External/cgal-python-bindings/src/alpha3_bindings/regular_release'


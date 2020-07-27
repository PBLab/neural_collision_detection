import pytest
import numpy as np

from ncd_post_process.neuron_to_vasc_dist_distrib import *
from ncd_post_process.aggregator import rotate, translate, swap_x_y



ZERO = np.array([[0, 0, 0]], dtype=np.float64)
X_ONLY = np.array([[1, 0, 0]], dtype=np.float64)
Y_ONLY = np.array([[0, 1, 0]], dtype=np.float64)
Z_ONLY = np.array([[0, 0, 1]], dtype=np.float64)
ROT_X_90 = np.array([90, 0, 0], dtype=np.float64)
ROT_Y_90 = np.array([0, 90, 0], dtype=np.float64)
ROT_Z_90 = np.array([0, 0, 90], dtype=np.float64)


@pytest.fixture()
def rotation_mat():
    def _make_rotation_mat(rot):
        return make_rotation_matrix(rot)
    return _make_rotation_mat

def test_zero_stays_zero(rotation_mat):
    rotated = rotate_table(ZERO, rotation_mat(ROT_X_90))
    np.testing.assert_array_almost_equal(ZERO, rotated)


def test_rotate_x_in_x(rotation_mat):
    rotated = rotate_table(X_ONLY, rotation_mat(ROT_X_90))
    np.testing.assert_array_almost_equal(X_ONLY, rotated)


def test_rotate_y_in_y(rotation_mat):
    rotated = rotate_table(Y_ONLY, rotation_mat(ROT_Y_90))
    np.testing.assert_array_almost_equal(Y_ONLY, rotated)


def test_yoav_rotate_y_in_y():
    coords = [[0, 1, 0, 1]]
    rotate(coords, ROT_Y_90)
    np.testing.assert_array_almost_equal([[0, 1, 0, 1]], coords)


def test_yoav_rotate_x_in_x():
    coords = [[1, 0, 0, 1]]
    rotate(coords, ROT_X_90)
    np.testing.assert_array_almost_equal([[1, 0, 0, 1]], coords)


def test_yoav_rotate_x_in_y():
    coords = [[1, 0, 0, 1]]
    rotate(coords, ROT_Y_90)
    np.testing.assert_array_almost_equal([[0, 0, -1, 1]], coords)


def test_rotate_x_in_y(rotation_mat):
    rotated = rotate_table(X_ONLY, rotation_mat(ROT_Y_90))
    np.testing.assert_array_almost_equal(-Z_ONLY, rotated)



def test_rotate_x_in_z(rotation_mat):
    rotated = rotate_table(X_ONLY, rotation_mat(ROT_Z_90))
    np.testing.assert_array_almost_equal(Y_ONLY, rotated)


def test_yoav_rotate_x_in_z():
    coords = [[1, 0, 0, 1]]
    rotate(coords, ROT_Z_90)
    np.testing.assert_array_almost_equal([[0, 1, 0, 1]], coords)


def test_yoav_rotate_arb():
    coords = [[1, 0.5, 0.1, 1]]
    rotate(coords, ROT_Y_90 + ROT_X_90)
    np.testing.assert_array_almost_equal([[0.1, 1., .5, 1]], coords)


def test_rotate_arb(rotation_mat):
    rotated = rotate_table(np.array([[1.0, 0.5, 0.1]]), rotation_mat(ROT_Y_90 + ROT_X_90))
    np.testing.assert_array_almost_equal([[0.1, 1.0, 0.5]], rotated)


def test_full_action_yoav_on_zero():
    neuron = [[0, 0, 0, 1]]
    swap_x_y(neuron)
    rotate(neuron, ROT_X_90)
    translate(neuron, [1, 1, 1])
    np.testing.assert_array_almost_equal([[1, 1, 1, 1]], neuron)


def test_full_action_on_zero(rotation_mat):
    neuron = pd.DataFrame({'x': [0.0], 'y': [0.0], 'z': [0.0], 'r': [1.0]})
    swapped = swap_xy(neuron).to_numpy()[:, :3]
    rotated = rotate_table(swapped, rotation_mat(ROT_X_90))
    translated = translate_table(rotated, np.array([[1, 1, 1]]))
    np.testing.assert_array_almost_equal(np.array([[1, 1, 1]]), translated)


def test_full_action_yoav_on_something():
    neuron = [[1, 0.5, 0.1, 1]]
    swap_x_y(neuron)
    rotate(neuron, ROT_X_90)
    translate(neuron, [1, 1, 1])
    np.testing.assert_array_almost_equal([[1.5, 0.9, 2, 1]], neuron)


def test_full_action_on_zero(rotation_mat):
    neuron = pd.DataFrame({'x': [1.0], 'y': [0.5], 'z': [0.1], 'r': [1.0]})
    swapped = swap_xy(neuron).to_numpy()[:, :3]
    rotated = rotate_table(swapped, rotation_mat(ROT_X_90))
    translated = translate_table(rotated, np.array([[1, 1, 1]]))
    np.testing.assert_array_almost_equal(np.array([[1.5, 0.9, 2]]), translated)

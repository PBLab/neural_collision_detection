import os
import pytest
import shutil
import hashlib
import inspect

#######################   consts   ###########################

TESTS_BASE_DIR = "_test_dir"
VASCULAR_PATH = "resources/vascular_test.obj"
NEURON_PATH = "resources/neuron_test.obj"
NCD_PATH = "../ncd"

#######################   pytest   ###########################

@pytest.fixture(scope="session", autouse=True)
def setup(request):
	print("Beginning is the")
	if os.path.exists(TESTS_BASE_DIR):
		shutil.rmtree(TESTS_BASE_DIR)
	os.mkdir(TESTS_BASE_DIR)
	request.addfinalizer(teardown)

def teardown():
	print ("End")

#######################   utils   ############################


def _verify_files(base_dir, files_to_verify):
	print(files_to_verify)
	for filename, md5 in files_to_verify.items():
		full_path = os.path.join(base_dir, filename)
		assert os.path.exists(full_path)
		file_md5 = hashlib.md5(open(full_path).read())
		assert file_md5.digest().encode("hex") == md5

def _verify_md5s(dir_name, cmd, files_to_verify):
	if not os.path.exists(dir_name):
		os.mkdir(dir_name)
	print(cmd)
	os.system(cmd)
	_verify_files(dir_name, files_to_verify)

def _create_centers(fname, centers):
	with open(fname, "wb") as f:
		for c in centers:
			f.write("%i, %i, %i\n" % c)


#######################   tests     ###########################


def test_verify():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	cmd = "{ncd} -m verify -V {vascular} -N {neuron} -o {test_dir} -r 10,20,30 -l 500,500,500".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir)
	files_to_verify = {
		"neuron_test.obj_500_500_500__10_20_30_collision.txt" 	: "9d7857900e0f072627cdb71fd14343fa",
		"neuron_test.obj_rotated_neuron.obj" 					: "c577b5dc1a7b5bd3f95b3406d7ac6970",
		"neuron_test.obj_cut_vascular.obj" 						: "2ccefa870c23db5e248e244cf434b61b"
		}

	_verify_md5s(test_dir, cmd, files_to_verify)



def test_regular_bound_check():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	test_file = "output.txt"
	center = "20,20,20"
	cmd = "{ncd} -V {vascular} -N {neuron} -m regular -o {test_dir} -f {test_file} -l {center}".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir,
								center = center,
								test_file = os.path.join(test_dir, test_file))
	files_to_verify = {
		test_file : "a128ecfcbb4bd5cb453c738628b3f0ba"
	}
	_verify_md5s(test_dir, cmd, files_to_verify)



def test_regular_minimal_only():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	test_file = "output.txt"
	center = "500,500,500"
	cmd = "{ncd} -V {vascular} -N {neuron} -m regular -o {test_dir} -f {test_file} -l {center} -z".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir,
								center = center,
								test_file = os.path.join(test_dir, test_file))
	files_to_verify = {
		test_file : "58c24057cf77ebaa43361bcfe27a4c1c"
	}
	_verify_md5s(test_dir, cmd, files_to_verify)


def test_regular_collision_limit():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	test_file = "output.txt"
	center = "300,300,300"
	cmd = "{ncd} -V {vascular} -N {neuron} -m regular -o {test_dir} -f {test_file} -l {center} -c 40".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir,
								center = center,
								test_file = os.path.join(test_dir, test_file))
	files_to_verify = {
		test_file : "4d458fecd04f36eb591c2f28d239f207"
	}
	_verify_md5s(test_dir, cmd, files_to_verify)


def test_collisions_files():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	test_file = "output.txt"
	center = "300,300,300"
	cmd = "{ncd} -V {vascular} -N {neuron} -m regular -o {test_dir} -f {test_file} -l {center} -s".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir,
								center = center,
								test_file = os.path.join(test_dir, test_file))
	files_to_verify = {
		test_file : "bf2c1cff871277958c8d01394777c1a6",
		"neuron_test.obj_300_300_300__0_-5_319_collision.txt" : "1e8d05a420b14554053e08221353ebfe",
		"neuron_test.obj_300_300_300__-1_1_320_collision.txt" : "a77a6ba7bbfee67957a18176438d0c68",
		"neuron_test.obj_300_300_300__-1_2_320_collision.txt" : "d5aa8b676c73c868028890b8b2db604e",
		"neuron_test.obj_300_300_300__1_2_321_collision.txt"  : "57fab89e9c437a408a5990aaccf00741",
		"neuron_test.obj_300_300_300__-1_2_323_collision.txt" : "0b16b8bbd659134f639efafe69b000d2",
		"neuron_test.obj_300_300_300__-2_3_323_collision.txt" : "e9f35280232a03c03e77beab6a9a125d",
		"neuron_test.obj_300_300_300__2_5_320_collision.txt"  : "4b00802d88ad2f57337ef82849c254c9",
		"neuron_test.obj_300_300_300__-3_5_322_collision.txt" : "1a99d0dc335efd96c04674177b75a931",
		"neuron_test.obj_300_300_300__-4_-2_329_collision.txt": "e213b7e30dc67261e446a457d7c9c3b6",
		"neuron_test.obj_300_300_300__-5_0_330_collision.txt" : "10187794339e7a60ef1f21b23c0e88b1"
	}
	_verify_md5s(test_dir, cmd, files_to_verify)


def test_regular():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	test_file = "output.txt"
	center = "500,500,500"
	cmd = "{ncd} -V {vascular} -N {neuron} -m regular -o {test_dir} -f {test_file} -l {center}".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir,
								center = center,
								test_file = os.path.join(test_dir, test_file))
	files_to_verify = {
		test_file : "0bf6b324eaada0907663b08267cc9519"
	}
	_verify_md5s(test_dir, cmd, files_to_verify)


def test_batch():
	test_dir = os.path.join(TESTS_BASE_DIR, inspect.currentframe().f_code.co_name)
	test_file = "output.txt"
	centers_fname = os.path.join(test_dir, "centers.txt")

	os.mkdir(test_dir)
	_create_centers(centers_fname, [(500,500,500), (400,400,400)])
	cmd = "{ncd} -V {vascular} -N {neuron} -m batch -o {test_dir} -f {test_file} -i {centers}".format(
								ncd = NCD_PATH,
								vascular = VASCULAR_PATH,
								neuron = NEURON_PATH,
								test_dir = test_dir,
								test_file = os.path.join(test_dir, test_file),
								centers = centers_fname)
	files_to_verify = {
		test_file : "3baff2db6e9e3ada1111cc1a81d307f5"
	}
	_verify_md5s(test_dir, cmd, files_to_verify)

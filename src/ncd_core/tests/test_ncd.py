import os
import pytest
import shutil
import hashlib
import inspect

#######################   consts   ###########################

TESTS_BASE_DIR = "_test_dir"
VASCULAR_PATH = "~/vascular/vascular_reduced_0.005.obj"
NEURON_PATH = "~/neurons/AP120410_s1c1.obj"
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
		"AP120410_s1c1.obj_500_500_500__10_20_30_collision.txt" : "9d7857900e0f072627cdb71fd14343fa",
		"AP120410_s1c1.obj_rotated_neuron.obj" 					: "c577b5dc1a7b5bd3f95b3406d7ac6970",
		"AP120410_s1c1.obj_cut_vascular.obj" 					: "2ccefa870c23db5e248e244cf434b61b"
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
		test_file : "c93fcc6207cedf081f90f22d7836bd69"	
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
		test_file : "54dd5c662a6d2b4700156b47ef1cd713"	
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
		test_file : "d6dfecbf7b4d400533e046b59510e8e5"	
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
		test_file : "23ad42fde44e2effddb77f35fab83e18"	
	}
	_verify_md5s(test_dir, cmd, files_to_verify)

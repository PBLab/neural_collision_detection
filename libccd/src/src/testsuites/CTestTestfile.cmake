# CMake generated Testfile for 
# Source directory: /data/simulated_morph_data/libccd/src/testsuites
# Build directory: /data/simulated_morph_data/libccd/src/src/testsuites
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
ADD_TEST(main "/data/simulated_morph_data/libccd/src/src/testsuites/main")
ADD_TEST(bench "/data/simulated_morph_data/libccd/src/src/testsuites/bench")
ADD_TEST(bench2 "/data/simulated_morph_data/libccd/src/src/testsuites/bench2")
SUBDIRS(cu)

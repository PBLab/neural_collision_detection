# CMake generated Testfile for 
# Source directory: /data/simulated_morph_data/fcl/test
# Build directory: /data/simulated_morph_data/fcl/build/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
ADD_TEST(test_fcl_auto_diff "/test_fcl_auto_diff")
ADD_TEST(test_fcl_box_box "/test_fcl_box_box")
ADD_TEST(test_fcl_broadphase_collision_1 "/test_fcl_broadphase_collision_1")
ADD_TEST(test_fcl_broadphase_collision_2 "/test_fcl_broadphase_collision_2")
ADD_TEST(test_fcl_broadphase_distance "/test_fcl_broadphase_distance")
ADD_TEST(test_fcl_bvh_models "/test_fcl_bvh_models")
ADD_TEST(test_fcl_capsule_box_1 "/test_fcl_capsule_box_1")
ADD_TEST(test_fcl_capsule_box_2 "/test_fcl_capsule_box_2")
ADD_TEST(test_fcl_capsule_capsule "/test_fcl_capsule_capsule")
ADD_TEST(test_fcl_cylinder_half_space "/test_fcl_cylinder_half_space")
ADD_TEST(test_fcl_collision "/test_fcl_collision")
ADD_TEST(test_fcl_constant_eps "/test_fcl_constant_eps")
ADD_TEST(test_fcl_distance "/test_fcl_distance")
ADD_TEST(test_fcl_frontlist "/test_fcl_frontlist")
ADD_TEST(test_fcl_general "/test_fcl_general")
ADD_TEST(test_fcl_generate_bvh_model_deferred_finalize "/test_fcl_generate_bvh_model_deferred_finalize")
ADD_TEST(test_fcl_geometric_shapes "/test_fcl_geometric_shapes")
ADD_TEST(test_fcl_math "/test_fcl_math")
ADD_TEST(test_fcl_profiler "/test_fcl_profiler")
ADD_TEST(test_fcl_shape_mesh_consistency "/test_fcl_shape_mesh_consistency")
ADD_TEST(test_fcl_signed_distance "/test_fcl_signed_distance")
ADD_TEST(test_fcl_simple "/test_fcl_simple")
ADD_TEST(test_fcl_sphere_box "/test_fcl_sphere_box")
ADD_TEST(test_fcl_sphere_capsule "/test_fcl_sphere_capsule")
ADD_TEST(test_fcl_sphere_cylinder "/test_fcl_sphere_cylinder")
ADD_TEST(test_fcl_sphere_sphere "/test_fcl_sphere_sphere")
SUBDIRS(geometry)
SUBDIRS(narrowphase)

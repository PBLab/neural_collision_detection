#pragma once

#include "model.hpp"
#include "result_object.hpp"
#include "cube.hpp"
#include "exception.hpp"

class CollisionManager
{
public:
	CollisionManager(const Model* m1, const Model* m2, const std::string& neuron_filename, int num_of_threads, int max_num_of_collisions,
				   	 const std::string& output_directory, bool minimal_only, bool bound_checks, bool should_output_collisions);
	~CollisionManager();
	void check_all_collisions(int x_pos, int y_pos, int z_pos, char main_axis, const std::string& output_filename);
	void check_all_collisions(const std::string& locations_filename, char main_axis, const std::string& output_filename);
	void check_single_collision(int x_pos, int y_pos, int z_pos, int x_r, int y_r, int z_r);
	const Model* m1() const;
	const Model* m2() const;
	std::string output_collision_points_single_collision(int x_pos, int y_pos, int z_pos, int x_r, int y_r, int z_r);
	bool should_output_collisions() const;

private:
	void check_all_collisions_at_location(int x_pos, int y_pos, int z_pos, char main_axis, const std::string& output_filename);

private:
	const Model * _m1;
	const Model * _m2;

	const FclModel * _fm1; // Vascular
	BoundingBox _fm1_bounding_box;
	const FclModel * _fm2; // Neuron
	Cube _fm2_cube;
	std::string _neuron_filename;
	std::string _output_directory;;
	int _num_of_threads;
	int _max_num_of_collisions;;
	bool _minimal_only = false;
	bool _bound_checks = true;
	bool _should_output_collision_files = true;
};


typedef struct thread_params
{
	ResultObject* result_object;
	CollisionManager* collision_manager;
	const FclModel* fm1; // Vascular
	const BoundingBox* fm1_bounding_box;
	const FclModel* fm2; // Neuron
	const Cube * fm2_cube;
	int x_pos;
	int y_pos;
	int z_pos;
	int num_of_col;

	int min_x;
	int max_x;
	int min_y;
	int max_y;
	int min_z;
	int max_z;

	int thread_id;
} thread_params_t;

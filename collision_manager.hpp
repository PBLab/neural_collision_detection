#pragma once

#include "model.hpp"
#include "result_object.hpp"
#include "exception.hpp"

class CollisionManager
{
public:
	CollisionManager(const Model* m1, const Model* m2, const std::string& neuron_filename, int num_of_threads);
	~CollisionManager();
	void check_all_collisions(int x_pos, int y_pos, int z_pos, char main_axis, int num_of_col, const std::string& output_filename);
	void check_all_collisions(const std::string& locations_filename, char main_axis, int num_of_col, const std::string& output_filename);
	void check_single_collision(int x_pos, int y_pos, int z_pos, int x_r, int y_r, int z_r, int num_of_col, const std::string& output_directory);
	const Model* m1() const;
	const Model* m2() const;

private:
	void check_all_collisions_at_location(int x_pos, int y_pos, int z_pos, char main_axis, int num_of_col, const std::string& output_filename,
										 FclModel* fm1, FclModel* fm2, const std::string& title);

private:
	const Model * _m1;
	const Model * _m2;
	std::string _neuron_filename;
	int _num_of_threads;
};


typedef struct thread_params
{
	ResultObject* result_object;
	CollisionManager* collision_manager;
	FclModel* fm1;
	FclModel* fm2;
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

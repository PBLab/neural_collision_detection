#pragma once
#include <memory>

#include "fcl.hpp"

class Model
{
public:
	Model(const std::string& vertices_filename, const std::string& triangles_filename);
	Model(const std::string& obj_filename);
	~Model();

	FclModel* fcl_model() const;
	void dump_to_file(const std::string& vertices_filename, const std::string& triangles_filename);
	void print_stats() const;
	void adjust_all(float x, float y, float z);
	void adjust_all();
	char get_longest_axis() const;

private:
	void read_from_file(const std::string& vertices_filename, const std::string& triangles_filename);
	void read_from_file(const std::string& obj_filename);
	void add_ver(float x1, float x2, float x3);
	void add_triangle(int pos1, int pos2, int pos3);
	void calc_min_max(int *min_x, int *max_x, int *min_y, int *max_y, int *min_z, int *max_z) const;

private:
	vector<Vec3f> _vertices;
	vector<Triangle> _triangles;
};

typedef std::shared_ptr<Model> ModelPtr;

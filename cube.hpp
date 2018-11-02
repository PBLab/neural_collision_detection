#pragma once

#include <memory>
#include "fcl.hpp"
#include "bounding_box.hpp"

class Cube
{
public:
	Cube();
	Cube(const BoundingBox& bb);

	Cube rotate_and_transform(const NativeMatrix& mat, int x, int y, int z) const;
	bool is_contained(const BoundingBox* bb) const;

private:
	void add_ver(float x, float y, float z);

private:
	vector<Vec3f> _vertices;
};

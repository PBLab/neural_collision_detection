#include "cube.hpp"

Cube::Cube()
{
}

Cube::Cube(const BoundingBox& bb)
{
	add_ver(bb.min_x, bb.min_y, bb.min_z);
	add_ver(bb.max_x, bb.min_y, bb.min_z);
	add_ver(bb.min_x, bb.max_y, bb.min_z);
	add_ver(bb.max_x, bb.max_y, bb.min_z);

	add_ver(bb.min_x, bb.min_y, bb.max_z);
	add_ver(bb.max_x, bb.min_y, bb.max_z);
	add_ver(bb.min_x, bb.max_y, bb.max_z);
	add_ver(bb.max_x, bb.max_y, bb.max_z);
}

Cube Cube::rotate_and_transform(const NativeMatrix& mat, int x, int y, int z) const
{
	Cube c;

	for(int i = 0; i < _vertices.size(); ++i)
	{
		const Vec3f& vertex = _vertices[i];
		double new_x = mat.values[0][0] * vertex[0] + 
				       mat.values[0][1] * vertex[1] + 
				       mat.values[0][2] * vertex[2];

		double new_y = mat.values[1][0] * vertex[0] + 
				       mat.values[1][1] * vertex[1] + 
				       mat.values[1][2] * vertex[2];

		double new_z = mat.values[2][0] * vertex[0] + 
				       mat.values[2][1] * vertex[1] + 
				       mat.values[2][2] * vertex[2];
		c.add_ver(new_x + x, new_y + y, new_z + z);
	}

	return c;
}

bool Cube::is_contained(const BoundingBox* bb) const
{
	for(int i = 0; i < _vertices.size(); ++i)
	{
		if (!bb->contains(_vertices[i][0], _vertices[i][1], _vertices[i][2]))
			return false;
	}
	return true;
}

void Cube::add_ver(float x, float y, float z)
{
	Vec3f vec1(x, y, z);
	_vertices.push_back(vec1);
}

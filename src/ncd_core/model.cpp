#include "model.hpp"
#include "exception.hpp"
#include "trace.hpp"

Model::Model()
{
}

Model::Model(const std::string& obj_filename)
{
	read_from_file(obj_filename);
}

Model::Model(const std::string& vertices_filename, const std::string& triangles_filename)
{
	read_from_file(vertices_filename, triangles_filename);
}

Model::Model(const Model& other)
{
	for(int i = 0; i < other._vertices.size(); ++i)
	{
		const Vec3f& new_vertex = other._vertices[i];
		add_ver(new_vertex[0], new_vertex[1], new_vertex[2]);
	}
	for(int i = 0; i < other._triangles.size(); ++i)
	{
		const Triangle& new_triangle = other._triangles[i];
		add_triangle(new_triangle[0], new_triangle[1], new_triangle[2]);
	}
}


Model::~Model()
{
}

FclModel* Model::fcl_model() const
{
	FclModel* m = new FclModel();

	// add the mesh data into the BVHFclModel structure
	m->beginModel();
	m->addSubModel(_vertices, _triangles);
	m->endModel();

	return m;
}

void Model::adjust_all()
{
	int i = 0;
	int max_x = 0;
	int max_y = 0;
	int max_z = 0;
	int min_x = 100000;
	int min_y = 100000;
	int min_z = 100000;
	for(i = 0; i < _vertices.size(); ++i)
	{
		if (_vertices[i](0) > max_x)
			max_x = _vertices[i](0);
		if (_vertices[i](1) > max_y)
			max_y = _vertices[i](1);
		if (_vertices[i](2) > max_z)
			max_z = _vertices[i](2);

		if (_vertices[i](0) < min_x)
			min_x = _vertices[i](0);
		if (_vertices[i](1) < min_y)
			min_y = _vertices[i](1);
		if (_vertices[i](2) < min_z)
			min_z = _vertices[i](2);
	}

	int adj_x = -1 * (max_x + min_x) / 2;
	int adj_y = -1 * (max_y + min_y) / 2;
	int adj_z = -1 * (max_z + min_z) / 2;

	adjust_all(adj_x, adj_y, adj_z);
}

void Model::adjust_all(float x, float y, float z)
{
	for(int i = 0; i < _vertices.size(); ++i)
	{
		_vertices[i][0] += x;
		_vertices[i][1] += y;
		_vertices[i][2] += z;
	}
}

void Model::add_ver(float x1, float x2, float x3)
{
	Vec3f vec1(x1, x2, x3);
	_vertices.push_back(vec1);
}

void Model::add_triangle(int pos1, int pos2, int pos3)
{
	Triangle triangle(pos1, pos2, pos3);
	_triangles.push_back(triangle);
}

void Model::read_from_file(const std::string& obj_filename)
{
	FILE * f = fopen(obj_filename.c_str(), "r");
	if (f == NULL)
	{
		throw Exception("failed opening file");
	}

	const char* line_template = "%c %f %f %f\n";
	char buff[1024];
	float a, b, c;
	char type;

	for(;;)
	{
		int ret = fscanf(f, line_template, &type, &a, &b, &c);
		if (ret <= 0)
			break;
		switch(type)
		{
			case 'v':
				add_ver(a, b, c);
				break;
			case 'f':
				add_triangle(a-1, b-1, c-1);
				break;
			default:
				LOG_DEBUG("unknown line type = %c %i\n", type, (int)type);
				break;
		}
	}
	fclose(f);
}

void Model::read_from_file(const std::string& vertices_filename, const std::string& triangles_filename)
{
	FILE * v_f = fopen(vertices_filename.c_str(), "r");
	if (v_f == NULL)
	{
		throw Exception("failed opening file");
	}

	const char* vertex_template = "%f,%f,%f\n";
	char buff[1024];
	float a, b, c;

	for(;;)
	{
		int ret = fscanf(v_f, vertex_template, &a, &b, &c);
		if (ret <= 0)
			break;
		add_ver(a, b, c);
	}
	fclose(v_f);

	FILE * t_f = fopen(triangles_filename.c_str(), "r");
	if (t_f == NULL)
	{
		throw Exception("failed opening file");
	}

	const char* triangle_template = "%i,%i,%i\n";
	int x, y, z;
	for(int i = 0;;++i)
	{
		int ret = fscanf(t_f, triangle_template, &x, &y, &z);
		if (ret <= 0)
			break;
		add_triangle(x, y, z);
		//static const int LIMIT = 5 * 10 * 1000;
		//if (i > LIMIT)
		//	break;
	}
	fclose(t_f);
}

void Model::dump_to_file(const std::string& output_filename) const
{
	FILE * file = fopen(output_filename.c_str(), "w");

	const char* vertex_template = "v %f %f %f\n";
	char buff[1024];

	int i = 0;
	for(i = 0; i < _vertices.size(); ++i)
	{
		int buflen = sprintf(buff, vertex_template, _vertices[i](0), _vertices[i](1), _vertices[i](2));
		fwrite(buff, buflen, sizeof(char), file);
	}

	const char* triangle_template = "f %i %i %i\n";
	for(i = 0; i < _triangles.size(); ++i)
	{
		int buflen = sprintf(buff, triangle_template, _triangles[i][0] + 1, _triangles[i][1] + 1, _triangles[i][2] + 1);
		fwrite(buff, buflen, sizeof(char), file);
	}
	fclose(file);
}

void Model::print_stats() const
{
	LOG_TRACE("\t=== Stats ===\n");
	LOG_TRACE("Num of vertices: %lu\n", _vertices.size());
	LOG_TRACE("Num of triangles: %lu\n", _triangles.size());

	float max_x, max_y, max_z, min_x, min_y, min_z;
	calc_min_max(&min_x, &max_x, &min_y, &max_y, &min_x, &max_z);

	LOG_TRACE("Max x: %f, max y: %f, max z: %f\n", max_x, max_y, max_z);
	LOG_TRACE("Min x: %f, min y: %f, min z: %f\n", min_x, min_y, min_z);
}

char Model::get_longest_axis() const
{
	float max_x, max_y, max_z, min_x, min_y, min_z;
	calc_min_max(&min_x, &max_x, &min_y, &max_y, &min_x, &max_z);

	float x_range = max_x - min_x;
	float y_range = max_y - min_y;
	float z_range = max_z - min_z;

	if (x_range > y_range && x_range > z_range)
		return 'x';
	if (y_range > z_range)
		return 'y';
	return 'z';
}

void Model::calc_min_max(float *min_x, float *max_x, float *min_y, float *max_y, float *min_z, float *max_z) const
{
	*min_x = _vertices[0](0);
	*max_x = _vertices[0](0);
	*min_y = _vertices[0](1);
	*max_y = _vertices[0](1);
	*min_z = _vertices[0](2);
	*max_z = _vertices[0](2);

	for(int i = 0; i < _vertices.size(); ++i)
	{
		if (_vertices[i](0) > *max_x)
			*max_x = _vertices[i](0);
		if (_vertices[i](1) > *max_y)
			*max_y = _vertices[i](1);
		if (_vertices[i](2) > *max_z)
			*max_z = _vertices[i](2);

		if (_vertices[i](0) < *min_x)
			*min_x = _vertices[i](0);
		if (_vertices[i](1) < *min_y)
			*min_y = _vertices[i](1);
		if (_vertices[i](2) < *min_z)
			*min_z = _vertices[i](2);
	}
}

void Model::rotate(const NativeMatrix& mat)
{
	for(int i = 0; i < _vertices.size(); ++i)
	{
		Vec3f& vertex = _vertices[i];
		double new_x = mat.values[0][0] * vertex[0] + 
				       mat.values[0][1] * vertex[1] + 
				       mat.values[0][2] * vertex[2];

		double new_y = mat.values[1][0] * vertex[0] + 
				       mat.values[1][1] * vertex[1] + 
				       mat.values[1][2] * vertex[2];

		double new_z = mat.values[2][0] * vertex[0] + 
				       mat.values[2][1] * vertex[1] + 
				       mat.values[2][2] * vertex[2];
		//LOG_INFO("x y z = %f %f %f\n", new_x, new_y, new_z);
		vertex[0] = new_x;
		vertex[1] = new_y;
		vertex[2] = new_z;
	}
}

Model Model::get_bounding_cube() const
{
	Model cube;
	BoundingBox bb = get_bounding_box();
	cube.add_ver(bb.min_x, bb.min_y, bb.min_z);
	cube.add_ver(bb.max_x, bb.min_y, bb.min_z);
	cube.add_ver(bb.max_x, bb.max_y, bb.min_z);
	cube.add_ver(bb.min_x, bb.max_y, bb.min_z);

	cube.add_ver(bb.min_x, bb.min_y, bb.max_z);
	cube.add_ver(bb.max_x, bb.min_y, bb.max_z);
	cube.add_ver(bb.max_x, bb.max_y, bb.max_z);
	cube.add_ver(bb.min_x, bb.max_y, bb.max_z);

	cube.add_triangle(1, 5, 6);
	cube.add_triangle(1, 6, 2);
	cube.add_triangle(2, 6, 7);
	cube.add_triangle(2, 7, 3);
	cube.add_triangle(3, 7, 8);
	cube.add_triangle(3, 8, 4);
	cube.add_triangle(4, 8, 5);
	cube.add_triangle(4, 5, 1);
	cube.add_triangle(6, 8, 7);
	cube.add_triangle(6, 5, 8);
	cube.add_triangle(4, 2, 3);
	cube.add_triangle(4, 1, 2);

	return cube;
}

BoundingBox Model::get_bounding_box() const
{
	BoundingBox res;
	calc_min_max(&res.min_x, &res.max_x, &res.min_y, &res.max_y, &res.min_z, &res.max_z);
	return res;
}

Model Model::get_sub_model(const BoundingBox& bb) const
{
	Model res;
	int next_idx = 0;
	int *new_indices = new int[_vertices.size()];
	for(int i = 0; i < _vertices.size(); ++i)
	{
		float x = _vertices[i](0);
		float y = _vertices[i](1);
		float z = _vertices[i](2);
		if (bb.contains(x, y, z))
		{
			new_indices[i] = next_idx;
			next_idx++;
			res.add_ver(x, y, z);
		}
		else
		{
			new_indices[i] = -1;
		}
	}
	for(int i = 0; i < _triangles.size(); ++i)
	{
		int a = _triangles[i][0];
		int b = _triangles[i][1];
		int c = _triangles[i][2];
		int new_a = new_indices[a];
		int new_b = new_indices[b];
		int new_c = new_indices[c];
		if (new_a == -1 || new_b == -1 || new_c == -1)
			continue;
		res.add_triangle(new_a, new_b, new_c);
	}

	delete[] new_indices;
	return res;
}

#include "model.hpp"
#include "exception.hpp"
#include "trace.hpp"

Model::Model(const std::string& obj_filename)
{
	read_from_file(obj_filename);
}

Model::Model(const std::string& vertices_filename, const std::string& triangles_filename)
{
	read_from_file(vertices_filename, triangles_filename);
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
				add_triangle(a, b, c);
				break;
			default:
				LOG_ERROR("type = %c %i\n", type, (int)type);
				throw Exception("Unknown line type");
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

void Model::dump_to_file(const std::string& vertices_filename, const std::string& triangles_filename)
{
	FILE * v_f = fopen(vertices_filename.c_str(), "w");

	const char* vertex_template = "%f,%f,%f\n";
	char buff[1024];

	int i = 0;
	for(i = 0; i < _vertices.size(); ++i)
	{
		int buflen = sprintf(buff, vertex_template, _vertices[i](0), _vertices[i](1), _vertices[i](2));
		fwrite(buff, buflen, sizeof(char), v_f);
	}
	fclose(v_f);

	FILE * t_f = fopen(triangles_filename.c_str(), "w");
	const char* triangle_template = "%i,%i,%i\n";
	for(i = 0; i < _triangles.size(); ++i)
	{
		int buflen = sprintf(buff, triangle_template, _triangles[i][0], _triangles[i][1], _triangles[i][2]);
		fwrite(buff, buflen, sizeof(char), t_f);
	}
	fclose(t_f);
}

void Model::print_stats() const
{
	LOG_TRACE("\t=== Stats ===\n");
	LOG_TRACE("Num of vertices: %lu\n", _vertices.size());
	LOG_TRACE("Num of triangles: %lu\n", _triangles.size());

	int max_x, max_y, max_z, min_x, min_y, min_z;
	calc_min_max(&min_x, &max_x, &min_y, &max_y, &min_x, &max_z);

	LOG_TRACE("Max x: %i, max y: %i, max z: %i\n", max_x, max_y, max_z);
	LOG_TRACE("Min x: %i, min y: %i, min z: %i\n", min_x, min_y, min_z);
}

char Model::get_longest_axis() const
{
	int max_x, max_y, max_z, min_x, min_y, min_z;
	calc_min_max(&min_x, &max_x, &min_y, &max_y, &min_x, &max_z);

	int x_range = max_x - min_x + 1;
	int y_range = max_y - min_y + 1;
	int z_range = max_z - min_z + 1;

	if (x_range > y_range && x_range > z_range)
		return 'x';
	if (y_range > z_range)
		return 'y';
	return 'z';
}

void Model::calc_min_max(int *min_x, int *max_x, int *min_y, int *max_y, int *min_z, int *max_z) const
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

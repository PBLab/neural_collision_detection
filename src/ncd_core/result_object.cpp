#include "result_object.hpp"
#include "exception.hpp"
#include "trace.hpp"
#include <string.h>

ResultObject::ResultObject(int min_x, int max_x, int min_y, int max_y, int min_z, int max_z, int x_loc, int y_loc, int z_loc)
:_x_min(min_x),
_x_max(max_x),
_y_min(min_y),
_y_max(max_y),
_z_min(min_z),
_z_max(max_z),
_x_loc(x_loc),
_y_loc(y_loc),
_z_loc(z_loc),
_current_elements(0)
{
	_x_size = _x_max - _x_min + 1;
	_y_size = _y_max - _y_min + 1;
	_z_size = _z_max - _z_min + 1;
	_result_array = new SingleResult**[_x_size];
	for(int i = 0; i < _x_size; ++i)
	{
		_result_array[i] = new SingleResult*[_y_size];
		for(int j = 0; j < _y_size; ++j)
		{
			_result_array[i][j] = new SingleResult[_z_size];
			for(int k = 0; k < _z_size; ++k)
			{
				_result_array[i][j][k].num_of_collisions = -1;
				_result_array[i][j][k].is_min = false;
				_result_array[i][j][k].output_filename[0] = '\0';
			}
		}
	}

	_total_elements = _x_size * _y_size * _z_size;
}

ResultObject::~ResultObject()
{
	for(int i = 0; i < _x_size; ++i)
	{
		for(int j = 0; j < _y_size; ++j)
		{
			delete[] _result_array[i][j];
		}
		delete[] _result_array[i];
	}
	delete[] _result_array;
}

void ResultObject::add_result(int x, int y, int z, int res)
{
	if (x < _x_min || y < _y_min || z < _z_min || x > _x_max || y > _y_max || z > _z_max)
	{
		LOG_DEBUG("x = %i, y = %i, z = %i\n"
				  "min_x = %i, min_y = %i, min_z = %i\n"
				  "max_x = %i, max_y = %i, max_z = %i\n",
				  x, y, z, _x_min, _y_min, _z_min, _x_max, _y_max, _z_max);
		throw Exception("add_result got wrong indices");
	}
	_result_array[x - _x_min][y - _y_min][z - _z_min].num_of_collisions = res;
	_current_elements++; // Not thread safe!
}

void ResultObject::write_to_file(const std::string& filename, const std::string& prefix, bool minimal_only)
{
	FILE* f = fopen(filename.c_str(), "a");
	if (f == NULL)
	{
		throw Exception("Failed opening output file");
	}

	for(int x = _x_min; x <= _x_max; ++x)
	{
		for(int y = _y_min; y <= _y_max; ++y)
		{
			for(int z = _z_min; z <= _z_max; ++z)
			{
				char str[1024];
				SingleResult* cur_result = &_result_array[x - _x_min][y - _y_min][z - _z_min];
				if (minimal_only && !cur_result->is_min)
					continue;
				snprintf(str, 1024, "%s,%i,%i,%i,%i,%i,%i,%i,%i,%s\n", prefix.c_str(), _x_loc, _y_loc, _z_loc,
											x, y, z,
											cur_result->num_of_collisions, cur_result->is_min, cur_result->output_filename);
				fwrite(str, strlen(str), 1, f);
			}
		}
	}
	fclose(f);
}

float ResultObject::get_percentage() const
{
	return (_current_elements*1.0) / _total_elements;
}

bool ResultObject::mark_min(int max_col)
{
	int min_x = 0;
	int min_y = 0;
	int min_z = 0;
	int min_res = max_col + 10;

	for(int x = _x_min; x <= _x_max; ++x)
	{
		for(int y = _y_min; y <= _y_max; ++y)
		{
			for(int z = _z_min; z <= _z_max; ++z)
			{
				SingleResult* cur_result = &_result_array[x - _x_min][y - _y_min][z - _z_min];
				if (!cur_result->is_min && cur_result->num_of_collisions < min_res)
				{
					min_res = cur_result->num_of_collisions;
					min_x = x;
					min_y = y;
					min_z = z;
				}
			}
		}
	}

	if (_result_array[min_x - _x_min][min_y - _y_min][min_z - _z_min].num_of_collisions < max_col)
	{
		_result_array[min_x - _x_min][min_y - _y_min][min_z - _z_min].is_min = true;
		return true;
	}
	return false;
}


int ResultObject::mark_mins(int amount, int max_col)
{
	for(int i = 0; i < amount; ++i)
	{
		if (!mark_min(max_col))
			return i;
	}
	return amount;
}

void ResultObject::for_each_result(result_callback_t callback, void* arg)
{
	for(int x = _x_min; x <= _x_max; ++x)
	{
		for(int y = _y_min; y <= _y_max; ++y)
		{
			for(int z = _z_min; z <= _z_max; ++z)
			{
				SingleResult* cur_result = &_result_array[x - _x_min][y - _y_min][z - _z_min];

				SingleResultCallbackParam params;
				params.x = _x_loc;
				params.y = _y_loc;
				params.z = _z_loc;
				params.r_x = x;
				params.r_y = y;
				params.r_z = z;
				params.single_result = cur_result;
				callback(arg, &params);
			}
		}
	}
}

void ResultObject::get_statistics(int max_col, int& total_results, int& oob_res,
							int& too_many_collisions_res, int& valid_res)
{
	total_results = 0;
	oob_res = 0;
	too_many_collisions_res = 0;
	valid_res = 0;
	for(int x = _x_min; x <= _x_max; ++x)
	{
		for(int y = _y_min; y <= _y_max; ++y)
		{
			for(int z = _z_min; z <= _z_max; ++z)
			{
				SingleResult* cur_result = &_result_array[x - _x_min][y - _y_min][z - _z_min];
				int col_num = cur_result->num_of_collisions;
				if (col_num < max_col)
					valid_res++;
				else if (col_num == max_col)
					too_many_collisions_res++;
				else
					oob_res++;
				total_results++;
			}
		}
	}


}

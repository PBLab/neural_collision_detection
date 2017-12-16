#include "result_object.hpp"
#include "exception.hpp"
#include "trace.hpp"
#include <string.h>

ResultObject::ResultObject(int min_x, int max_x, int min_y, int max_y, int min_z, int max_z)
:_x_min(min_x),
_x_max(max_x),
_y_min(min_y),
_y_max(max_y),
_z_min(min_z),
_z_max(max_z),
_current_elements(0)
{
	_x_size = _x_max - _x_min + 1;
	_y_size = _y_max - _y_min + 1;
	_z_size = _z_max - _z_min + 1;
	_result_array = new int**[_x_size];
	for(int i = 0; i < _x_size; ++i)
	{
		_result_array[i] = new int*[_y_size];
		for(int j = 0; j < _y_size; ++j)
		{
			_result_array[i][j] = new int[_z_size];
			for(int k = 0; k < _z_size; ++k)
			{
				_result_array[i][j][k] = -1;
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
		LOG_ERROR("x = %i, y = %i, z = %i\n", x, y, z);		
		LOG_ERROR("min_x = %i, min_y = %i, min_z = %i\n", _x_min, _y_min, _z_min);		
		LOG_ERROR("max_x = %i, max_y = %i, max_z = %i\n", _x_max, _y_max, _z_max);		
		throw Exception("add_result got wrong indices");
	}
	_result_array[x - _x_min][y - _y_min][z - _z_min] = res;
	_current_elements++; // Not thread safe!
}

void ResultObject::write_to_file(const std::string& filename, const std::string& title)
{
	FILE* f = fopen(filename.c_str(), "a");
	if (f == NULL)
	{
		throw Exception("Failed opening output file");
	}

	if (title.length() != 0)
	{
		char str[1024];
		snprintf(str, 1024, "========== %s ==========\n", title.c_str());
		fwrite(str, strlen(str), 1, f);
	}

	for(int x = _x_min; x <= _x_max; ++x)
	{
		for(int y = _y_min; y <= _y_max; ++y)
		{
			for(int z = _z_min; z <= _z_max; ++z)
			{
				char str[1024];
				snprintf(str, 1024, "%i,%i,%i : %i\n", x, y, z,
											_result_array[x - _x_min][y - _y_min][z - _z_min]);
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

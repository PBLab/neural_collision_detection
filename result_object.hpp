#pragma once

#include <string>

typedef struct SingleResult_s
{
	int num_of_collisions;
	bool is_min;
} SingleResult;

class ResultObject
{
	public:
		ResultObject(int min_x, int max_x, int min_y, int max_y, int min_z, int max_z, int x_loc, int y_loc, int z_loc);
		~ResultObject();

		void add_result(int x, int y, int z, int res);
		void write_to_file(const std::string& filename, const std::string& prefix);
		float get_percentage() const;

	private:
		SingleResult*** _result_array;
		int _total_elements;
		int _current_elements;

		int _x_loc;
		int _y_loc;
		int _z_loc;

		int _x_min;
		int _x_max;

		int _y_min;
		int _y_max;

		int _z_min;
		int _z_max;

		int _x_size;
		int _y_size;
		int _z_size;
};

#pragma once

#include <string>

#define OUTPUT_FILENAME_LENGTH 256

typedef struct SingleResult_s
{
	int num_of_collisions;
	bool is_min;
	char output_filename[OUTPUT_FILENAME_LENGTH];
} SingleResult;

typedef struct SingleResultCallbackParam_s
{
	int x;
	int y;
	int z;
	int r_x;
	int r_y;
	int r_z;
	SingleResult* single_result;
}SingleResultCallbackParam;

typedef void (*result_callback_t)(void* arg, SingleResultCallbackParam * params);

class ResultObject
{
	public:
		ResultObject(int min_x, int max_x, int min_y, int max_y, int min_z, int max_z, int x_loc, int y_loc, int z_loc);
		~ResultObject();

		void add_result(int x, int y, int z, int res);
		void write_to_file(const std::string& filename, const std::string& prefix, bool minimal_only = false);
		float get_percentage() const;
		int mark_mins(int amount, int max_col);
		void for_each_result(result_callback_t callback, void* arg);
		void get_statistics(int max_col, int& total_results, int& oob_res,
							int& too_many_collisions_res, int& valid_res);


	private:
		bool mark_min(int max_col);

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

#pragma once

#include <linux/limits.h>
#include <time.h>


class Program
{
public:
	Program(int argc, char** argv);
	~Program();

	void logic();

private:
	void parse_args(int argc, char** argv);
	void verify_args();
	void print_usage();

private:
	char _vascular_path[PATH_MAX] = {0};
	char _neural_path[PATH_MAX] = {0};
	char _output_file[PATH_MAX] = {0};
	int _x = 0;
	int _y = 0;
	int _z = 0;
	char _main_axis = 'z';
	int _num_of_threads = 10;
	int _num_of_collisions = 20000;
	int _use_obj = true;
	int _verbose = 1;

	time_t _start_time;
};

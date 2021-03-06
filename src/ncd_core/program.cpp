#include "program.hpp"
#include "model.hpp"
#include "collision_manager.hpp"
#include "exception.hpp"
#include "trace.hpp"
#include <getopt.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>


Program::Program(int argc, char** argv)
{
	_start_time = time(NULL);
	parse_args(argc, argv);
	verify_args();
}

Program::~Program()
{
}


ModelPtr create_obj_model(char* path)
{
	return ModelPtr(new Model(path));
}

std::string get_file_name_from_path(const std::string& path)
{
	size_t i = path.rfind('/', path.length());
	if (i != string::npos)
		return(path.substr(i+1, path.length() - i));

	return path;
}


void Program::logic()
{
	ModelPtr vascular_model;
	ModelPtr neural_model;
	vascular_model = create_obj_model(_vascular_path);
	neural_model = create_obj_model(_neural_path);

	vascular_model->print_stats();
	neural_model->print_stats();

	struct stat st = {0};
	if (stat(_output_directory, &st) == -1)
	{
		LOG_INFO("Creating output directory\n");
		mkdir(_output_directory, 0700);
	}
	CollisionManager collision_manager(&*vascular_model, &*neural_model, get_file_name_from_path(_neural_path), _num_of_threads, _num_of_collisions, _output_directory, _minimal_only, _bound_checks, _should_output_collisions, _should_rotate);
	if (_mode == MODE__VERIFY)
	{
		collision_manager.check_single_collision(_x, _y, _z, _r_x, _r_y, _r_z);
	}
	else
	{
		// Ignore ret value
		unlink(_output_file);
		if (_mode == MODE__REGULAR)
		{
			collision_manager.check_all_collisions(_x, _y, _z, _main_axis, _output_file);
		}
		else if (_mode == MODE__BATCH)
		{
			collision_manager.check_all_collisions(_input_file, _main_axis, _output_file);
		}
	}

	LOG_INFO("Total run time: %i minutes\n", (time(NULL) - _start_time) / 60);
}

void Program::verify_args()
{
	if (strlen(_vascular_path) == 0)
		throw Exception("Vascular path must be set");
	if (strlen(_neural_path) == 0)
		throw Exception("Neural path must be set");
	switch(_mode)
	{
	case MODE__REGULAR:
		if (strlen(_output_file) == 0)
			throw Exception("Output file path must be set in regular mode");
		if (strlen(_input_file) > 0)
			throw Exception("Can't use input file in regular mode");
		break;

	case MODE__VERIFY:
		if (strlen(_output_file) != 0)
			throw Exception("Output file path must NOT be set in verify mode");
		if (strlen(_input_file) > 0)
			throw Exception("Can't use input file in verify mode");
		if (_minimal_only)
			throw Exception("Can't use minimal only in verify mode");

		_should_output_collisions = true;
		break;

	case MODE__BATCH:
		if (strlen(_output_file) == 0)
			throw Exception("Output file path must be set in batch mode");
		if (strlen(_input_file) == 0)
			throw Exception("Input file path must be set in batch mode");
		if (_x != 0 || _y != 0 || _z != 0)
			throw Exception("-l can't be used in batch mode");
		break;

	default:
		throw Exception("Unknown mode");
	}

	if (strlen(_output_directory) == 0)
		throw Exception("Output dir path must be set");

	if (_num_of_threads <= 0 or _num_of_threads > 360)
		throw Exception("Num of threads must be between 1 and 360");

	if (_main_axis != 'x' && _main_axis != 'y' && _main_axis != 'z')
		throw Exception("Main axis must be one of x, y, z");
}

void Program::parse_args(int argc, char** argv)
{
	int c;
	for(;;)
	{
		int option_index = 0;
		static struct option long_options[] = {
			{"help", no_argument, 0, 'h'},
			{"vascular-path", required_argument, 0, 'V'},
			{"neural-path", required_argument, 0, 'N'},
			{"threads", required_argument, 0, 't'},
			{"collisions", required_argument, 0, 'c'},
			{"input-file", required_argument, 0, 'i'},
			{"main-axis", required_argument, 0, 'm'},
			{"output-file", required_argument, 0, 'f'},
			{"rotation", required_argument, 0, 'r'},
			{"output-directory", required_argument, 0, 'o'},
			{"location", required_argument, 0, 'l'},
			{"minimal-only", required_argument, 0, 'z'},
			{"bound-checks", required_argument, 0, 'b'},
			{"should-output-collisions", required_argument, 0, 's'},
			{0, 0, 0, 0}
		};

		c = getopt_long(argc, argv, "f:V:N:t:i:c:qzbsvnl:m:r:o:h", long_options, &option_index);
		if (c == -1)
			break;

		switch(c)
		{
		case 'V':
			strncpy(_vascular_path, optarg, PATH_MAX);
			break;
		case 'N':
			strncpy(_neural_path, optarg, PATH_MAX);
			break;
		case 'f':
			strncpy(_output_file, optarg, PATH_MAX);
			break;
		case 't':
			_num_of_threads = atoi(optarg);
			break;
		case 'c':
			_num_of_collisions = atoi(optarg);
			break;
		case 'i':
			strncpy(_input_file, optarg, PATH_MAX);
			break;
		case 'l':
			parse_triplet(optarg, &_x, &_y, &_z);
			break;
		case 'm':
			if (strcmp(optarg, "regular") == 0)
				_mode = MODE__REGULAR;
			else if (strcmp(optarg, "verify") == 0)
				_mode = MODE__VERIFY;
			else if (strcmp(optarg, "batch") == 0)
				_mode = MODE__BATCH;
			break;
		case 'a':
			_main_axis = optarg[0];
			break;
		case 'v':
			_verbose++;
			set_verbosity(_verbose);
			break;
		case 'q':
			set_verbosity(0);
			break;
		case 'r':
			parse_triplet(optarg, &_r_x, &_r_y, &_r_z);
			break;
		case 'o':
			strncpy(_output_directory, optarg, PATH_MAX);
			break;
		case 'z':
			_minimal_only = true;
			break;
		case 'b':
			_bound_checks = false;
			break;
		case 's':
			_should_output_collisions = true;
			break;
		case 'n':
			_should_rotate = false;
			break;
		case '?':
		case 'h':
		default:
			print_usage();
			throw Exception("Usage");
		}
	}
}

void Program::parse_triplet(char* optarg, int* a, int* b, int* c)
{
	char param[128];
	strcpy(param, optarg);
	char* first_coma = strchr(param, ',');
	if (first_coma == NULL)
		throw Exception("Invalid triplet format");
	char* second_coma = strchr(first_coma + 1, ',');
	if (second_coma == NULL)
		throw Exception("Invalid triplet format");

	*first_coma = '\0';
	*second_coma = '\0';
	*a = atoi(param);
	*b = atoi(first_coma + 1);
	*c = atoi(second_coma + 1);
}

void Program::print_usage()
{
	printf("Usage: ./ncd [OPTIONS]\n");
	printf("\t-h, --help\t\tPrint this help and exit\n");
	printf("\t-m, --mode\t\tRunning mode [regular, verify, batch]\n");
	printf("\t-V, --vascular-path\tPath to vascular data directory\n");
	printf("\t-N, --neural-path\tPath to neural data directory\n");
	printf("\t-t, --threads\t\tNumber of threads to use, between 1-360 [default - 10]\n");
	printf("\t-a, --main-axis\t\tMain axis for rotation [default - z]\n");
	printf("\t-o, --output-directory\tOutput directory\n");
	printf("\t-f, --output-file\tOutput filename [Regular/Batch mode]\n");
	printf("\t-r, --rotation\t\tRotation [x,y,z] [Verify mode]\n");
	printf("\t-i, --input-file\tInput file of locations [Batch mode]\n");
	printf("\t-l, --location\t\tLocation of neuron [Regular/Verify mode]\n");
	printf("\t-c, --collisions\tNumber of maximum collisions to check [default - 2000]\n");
	printf("\t-z, --minimal-only\tStore only minimal rotations in output file [Regular/Batch mode]\n");
	printf("\t-b, --bound-checks\tDon't eliminate results with bounds violation [Regular/Batch mode] [default - eliminate]\n");
	printf("\t-s, --output-collisions\tOutput files containing the collision points [Regular/Batch mode] [default - don't output]\n");
	printf("\t-n, --no-rotation\tDon't rotate the neuron [default - rotate]\n");
	printf("\t-v\t\t\tverbose (can use multiple times)\n");
	printf("\t-q\t\t\tquiet\n");
}

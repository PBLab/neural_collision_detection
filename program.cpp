#include "program.hpp"
#include "model.hpp"
#include "collision_manager.hpp"
#include "exception.hpp"
#include "trace.hpp"
#include <getopt.h>
#include <stdio.h>
#include <string.h>


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

ModelPtr create_csv_model(char* path)
{
	char vertices[PATH_MAX];
	char faces[PATH_MAX];

	strcpy(vertices, path);
	strcat(vertices, "/vertices.csv");

	strcpy(faces, path);
	strcat(faces, "/faces.csv");

	return ModelPtr(new Model(vertices, faces));
}

void Program::logic()
{
	ModelPtr vascular_model;
	ModelPtr neural_model;
	if (_use_obj)
	{
		vascular_model = create_obj_model(_vascular_path);
		neural_model = create_obj_model(_neural_path);
	}
	else
	{
		vascular_model = create_csv_model(_vascular_path);
		neural_model = create_csv_model(_neural_path);
	}

	//neural_model->adjust_all();
	//neural_model.adjust_all(-1 * _x, -1 * _y, -1 * _z);

	vascular_model->print_stats();
	neural_model->print_stats();

	if (_main_axis == '\0')
	{
		_main_axis = neural_model->get_longest_axis();
		LOG_INFO("Longest axis: %c\n", _main_axis);
	}

	CollisionManager collision_manager(&*vascular_model, &*neural_model, _num_of_threads);
	collision_manager.check_all_collisions(_x, _y, _z, _main_axis, _num_of_collisions, _output_file);

	LOG_INFO("Total run time: %i minutes\n", (time(NULL) - _start_time) / 60);
}

void Program::verify_args()
{
	if (_x <= 0)
		throw Exception("x must be set");
	if (_y <= 0)
		throw Exception("y must be set");
	if (_z <= 0)
		throw Exception("z must be set");

	if (strlen(_vascular_path) == 0)
		throw Exception("Vascular path must be set");
	if (strlen(_neural_path) == 0)
		throw Exception("Neural path must be set");
	if (strlen(_output_file) == 0)
		throw Exception("Output file path must be set");

	if (_num_of_threads <= 0 or _num_of_threads > 360)
		throw Exception("Num of threads must be between 1 and 360");

	if (_num_of_collisions <= 0)
		throw Exception("Num of collisions must be positive");

	if (_main_axis != '\0' && _main_axis != 'x' && _main_axis != 'y' && _main_axis != 'z')
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
			{"main-axis", required_argument, 0, 'm'},
			{"use-obj", required_argument, 0, 'o'},
			{"output-file", required_argument, 0, 'f'},
			{0, 0, 0, 0}
		};

		c = getopt_long(argc, argv, "f:V:N:t:c:qvx:y:z:m:h", long_options, &option_index);
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
		case 'x':
			_x = atoi(optarg);
			break;
		case 'y':
			_y = atoi(optarg);
			break;
		case 'z':
			_z = atoi(optarg);
			break;
		case 'm':
			_main_axis = optarg[0];
			break;
		case 'o':
			_use_obj = true;
			break;
		case 'v':
			_verbose++;
			set_verbosity(_verbose);
			break;
		case 'q':
			set_verbosity(0);
			break;
		case '?':
		case 'h':
		default:
			print_usage();
			throw Exception("Usage");
		}
	}
}

void Program::print_usage()
{
	printf("Usage: ./fcl [OPTIONS]\n");
	printf("\t-h, --help\t\tPrint this help and exit\n");
	printf("\t-V, --vascular-path\tPath to vascular data directory\n");
	printf("\t-N, --neural-path\tPath to neural data directory\n");
	printf("\t-t, --threads\t\tNumber of threads to use, between 1-360 [default - 10]\n");
	printf("\t-c, --collisions\tNumber of maximum collisions to check [default - 20000]\n");
	printf("\t-m, --main-axis\t\tMain axis for rotation [default - z]\n");
	printf("\t-f, --output-file\t\tOutput filename\n");
	printf("\t-x\t\t\tx coordinate of the center of the neuron\n");
	printf("\t-y\t\t\ty coordinate of the center of the neuron\n");
	printf("\t-z\t\t\tz coordinate of the center of the neuron\n");
	printf("\t-v\t\t\tverbose (can use multiple times)\n");
	printf("\t-q\t\t\tquiet\n");
}

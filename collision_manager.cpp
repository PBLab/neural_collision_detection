#include "collision_manager.hpp"
#include "collision.hpp"
#include "trace.hpp"
#include <pthread.h>

static void* thread_main_impl(thread_params_t* params);
static void* thread_main(void* arg);

CollisionManager::CollisionManager(const Model* m1, const Model* m2, const std::string& neuron_filename, int num_of_threads, const std::string& output_directory)
{
	_m1 = m1;
	_m2 = m2;
	_num_of_threads = num_of_threads;
	_neuron_filename = neuron_filename;
	_output_directory = output_directory;

	LOG_INFO("Creating model1...\n");
	_fm1 = _m1->fcl_model();
	LOG_INFO("\tDone.\n");
	LOG_INFO("Creating model2...\n");
	_fm2 = _m2->fcl_model();
	LOG_INFO("\tDone.\n");
}

CollisionManager::~CollisionManager()
{
	delete _fm1;
	delete _fm2;
}


static void* thread_main(void* arg)
{
	thread_params_t* params = (thread_params_t*)arg;
	try
	{
		thread_main_impl(params);
	}
	catch(const Exception& exp)
	{
		LOG_ERROR("Exception in thread #%i: %s\n", params->thread_id, exp.msg().c_str());
	}
	catch(...)
	{
		LOG_ERROR("Unknown exception in thread #%i\n", params->thread_id);
	}
}

static void report_progress(ResultObject* res)
{
	static int last_percentage = 0;
	int cur_percentage = (int)(res->get_percentage() * 100);
	if (cur_percentage == last_percentage)
	{
		return;
	}

	if (cur_percentage % 10 == 0)
		LOG_INFO("Completed %i%\n", cur_percentage);
	else
		LOG_TRACE("Completed %i%\n", cur_percentage);
	last_percentage = cur_percentage;
}

static void* thread_main_impl(thread_params_t* params)
{
	LOG_TRACE("Thread main #%i! min_x -> max_x: %i -> %i. Creating models...\n",
					params->thread_id, params->min_x, params->max_x);
	const FclModel * fm1 = params->fm1;
	const FclModel * fm2 = params->fm2;
	int id = params->thread_id;
	
	for(int x = params->min_x; x <= params->max_x; ++x)
	{
		for(int y = params->min_y; y <= params->max_y; ++y)
		{
			for(int z = params->min_z; z <= params->max_z; ++z)
			{
				static PointsVector* IGNORE_COLLISIONS_LOCATIONS = NULL;
				int num_of_collisions =
						Collision::check_a_collision(fm1,
													 fm2,
													 params->x_pos,
													 params->y_pos,
													 params->z_pos,
													 x,
													 y,
													 z,
													 params->num_of_col,
													 IGNORE_COLLISIONS_LOCATIONS);
				LOG_DEBUG("(%i):\t(%i,\t%i,\t%i)\t=\t%i\n", id, x, y, z, num_of_collisions);
				params->result_object->add_result(x, y, z, num_of_collisions);
				if (id == 0)
					report_progress(params->result_object);
			} 
		}
	}
	LOG_TRACE("Thread #%i Finished\n", id);
	return NULL;
}


void calc_ranges(char main_axis, int* min_x, int* max_x, int* min_y, int* max_y, int* min_z, int* max_z)
{
	switch(main_axis)
	{
	case 'x':
		*min_x = 0;
		*max_x = 359;
		*min_y = *min_z = -5;
		*max_y = *max_z = 5;
		break;
	case 'y':
		*min_y = 0;
		*max_y = 359;
		*min_x = *min_z = -5;
		*max_x = *max_z = 5;
		break;
	case 'z':
		*min_z = 0;
		*max_z = 359;
		*min_x = *min_y = -5;
		*max_x = *max_y = 5;
		break;
	default:
		throw Exception("Invalid main axis");
	};
}

void write_collisions_to_file(const std::string& filename, const PointsVector& res, int num_of_collisions)
{
	FILE* f = fopen(filename.c_str(), "w");
	if (f == NULL)
	{
		throw Exception("Failed opening output file");
	}

	for(int i = 0; i < num_of_collisions; ++i)
	{
		char str[1024];
		snprintf(str, 1024, "%f,%f,%f\n", res[i][0], res[i][1], res[i][2]);
		fwrite(str, strlen(str), 1, f);
	}
	fclose(f);
}

void CollisionManager::check_single_collision(int x_pos, int y_pos, int z_pos, int x_r, int y_r, int z_r, int num_of_col)
{
	LOG_INFO("Checking single collision...\n");
	output_collision_points_single_collision(x_pos, y_pos, z_pos, x_r, y_r, z_r, num_of_col);

	Model neuron = *_m2;
	NativeMatrix mat = Collision::calc_native_matrix(x_r, y_r, z_r);
	neuron.rotate(mat);
	neuron.adjust_all(x_pos, y_pos, z_pos);
	std::string output_rotated_neuron = _output_directory + "/" + _neuron_filename + "_rotated_neuron.obj";
	neuron.dump_to_file(output_rotated_neuron);

	BoundingBox bb = neuron.get_bounding_box();
	Model vascular = _m1->get_sub_model(bb);
	std::string output_cut_vascular = _output_directory + "/" + _neuron_filename + "_cut_vascular.obj";
	vascular.dump_to_file(output_cut_vascular);
}

std::string CollisionManager::output_collision_points_single_collision(int x_pos, int y_pos, int z_pos, int x_r, int y_r, int z_r, int num_of_col)
{
	PointsVector res;
	int num_of_collisions =
			Collision::check_a_collision(_fm1,
										 _fm2,
										 x_pos,
										 y_pos,
										 z_pos,
										 x_r,
										 y_r,
										 z_r,
										 num_of_col,
										 &res);
	LOG_INFO("Num of collisions is: %i\n", num_of_collisions);
	std::string output_collision_points = _output_directory + "/" + _neuron_filename + "_collision.txt";
	write_collisions_to_file(output_collision_points, res, num_of_collisions);

	return output_collision_points;
}

void CollisionManager::check_all_collisions_at_location(int x_pos, int y_pos, int z_pos, char main_axis, int num_of_col, const std::string& output_filename)
{
	LOG_INFO("Checking collisions at (%i, %i, %i), using %i threads\n", x_pos, y_pos, z_pos, _num_of_threads);
	int min_x, max_x, min_y, max_y, min_z, max_z;
	calc_ranges(main_axis, &min_x, &max_x, &min_y, &max_y, &min_z, &max_z);
	//ResultObject res(-5, 5, -5, 5, 0, 359);
	ResultObject res(min_x, max_x, min_y, max_y, min_z, max_z, x_pos, y_pos, z_pos);

	pthread_t * thread_ids = new pthread_t[_num_of_threads];
	int z_range = max_z - min_z + 1;
	int next_z = min_z;
	thread_params_t * all_params = new thread_params[_num_of_threads];
	for (int i = 0; i < _num_of_threads; ++i)
	{
		LOG_TRACE("Preparing thread #%i\n", i);
		thread_params_t* params = &all_params[i];
		params->thread_id = i;
		params->result_object = &res;
		//params->collision_manager = this;
		params->fm1 = _fm1;
		params->fm2 = _fm2;
		params->x_pos = x_pos;
		params->y_pos = y_pos;
		params->z_pos = z_pos;
		params->num_of_col = num_of_col;

		params->min_z = next_z;
		params->max_z = next_z + z_range / _num_of_threads - 1;
		if (i == _num_of_threads - 1)
			params->max_z = max_z;
		next_z = params->max_z + 1;

		params->min_x = min_x;
		params->max_x = max_x;
		params->min_y = min_y;
		params->max_y = max_y;
	}

	for (int i = 0; i < _num_of_threads; ++i)\
	{
		thread_params_t* params = &all_params[i];
		LOG_TRACE("About to create thread #%i...\n", i);
		int ret = pthread_create(&thread_ids[i], NULL, thread_main, params);
		if (ret < 0)
		{
			throw Exception("Error in pthread_create");
		}
		LOG_TRACE(" > Thread created\n");
	}

	void* ignores_res;

	for(int i = 0; i < _num_of_threads; ++i)
	{
		LOG_TRACE("============ About to join thread #%i ============\n", i);
		int ret = pthread_join(thread_ids[i], &ignores_res);
		if (ret != 0)
		{
			throw Exception("Error in pthread_join");
		}
		LOG_TRACE("pthread_join #%i returned\n", i);
	}

	res.mark_mins(10);

	res.write_to_file(output_filename, _neuron_filename);
}

void CollisionManager::check_all_collisions(const std::string& locations_filename, char main_axis, int num_of_col, const std::string& output_filename)
{
	FILE * f = fopen(locations_filename.c_str(), "r");
	if (f == NULL)
	{
		throw Exception("failed opening locations file");
	}

	const char* line_template = "%i,%i,%i\n";
	char buff[1024];
	int x, y, z;

	for(;;)
	{
		int ret = fscanf(f, line_template, &x, &y, &z);
		if (ret <= 0)
			break;
		check_all_collisions_at_location(x, y, z, main_axis, num_of_col, output_filename);
	}
	fclose(f);
	LOG_INFO("Done!\n");
}

void CollisionManager::check_all_collisions(int x_pos, int y_pos, int z_pos, char main_axis, int num_of_col, const std::string& output_filename)
{
	LOG_INFO("Creating model1...\n");
	check_all_collisions_at_location(x_pos, y_pos, z_pos, main_axis, num_of_col, output_filename);
	LOG_INFO("Done!\n");
}


const Model* CollisionManager::m1() const
{
	return _m1;
}

const Model* CollisionManager::m2() const
{
	return _m2;
}

#include "collision_manager.hpp"
#include "collision.hpp"
#include "trace.hpp"
#include <pthread.h>

static void* thread_main_impl(thread_params_t* params);
static void* thread_main(void* arg);

CollisionManager::CollisionManager(const Model* m1, const Model* m2, int num_of_threads)
{
	_m1 = m1;
	_m2 = m2;
	_num_of_threads = num_of_threads;
}

CollisionManager::~CollisionManager()
{
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

	LOG_INFO("Completed %i%\n", cur_percentage);
	last_percentage = cur_percentage;
}

static void* thread_main_impl(thread_params_t* params)
{
	LOG_INFO("Thread main #%i! min_x -> max_x: %i -> %i. Creating models...\n",
					params->thread_id, params->min_x, params->max_x);
	FclModel * fm1 = params->fm1;
	FclModel * fm2 = params->fm2;
	int id = params->thread_id;
	int cnt = 0;
	
	for(int x = params->min_x; x <= params->max_x; ++x)
	{
		for(int y = params->min_y; y <= params->max_y; ++y)
		{
			for(int z = params->min_z; z <= params->max_z; ++z)
			{
				int num_of_collisions = Collision::check_a_collision(fm1,
																	 fm2,
																	 params->x_pos,
																	 params->y_pos,
																	 params->z_pos,
																	 x,
																	 y,
																	 z,
																	 params->num_of_col);
				if (cnt % 121 == 0) // || num_of_collisions != params->num_of_col)
					LOG_TRACE("(%i):\t(%i,\t%i,\t%i)\t=\t%i\n", id, x, y, z, num_of_collisions);
				LOG_DEBUG("(%i):\t(%i,\t%i,\t%i)\t=\t%i\n", id, x, y, z, num_of_collisions);
				params->result_object->add_result(x, y, z, num_of_collisions);
				cnt++;
				if (id == 0)
					report_progress(params->result_object);
			} 
		}
	}
	LOG_INFO("Thread #%i Finished\n", id);
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

void CollisionManager::check_all_collisions(int x_pos, int y_pos, int z_pos, char main_axis, int num_of_col, const std::string& output_filename)
{
	int min_x, max_x, min_y, max_y, min_z, max_z;
	calc_ranges(main_axis, &min_x, &max_x, &min_y, &max_y, &min_z, &max_z);
	//ResultObject res(-5, 5, -5, 5, 0, 359);
	ResultObject res(min_x, max_x, min_y, max_y, min_z, max_z);

	LOG_INFO("Num of threads: %i\n", _num_of_threads);

	pthread_t * thread_ids = new pthread_t[_num_of_threads];
	int z_range = max_z - min_z + 1;
	int next_z = min_z;
	thread_params_t * all_params = new thread_params[_num_of_threads];
	FclModel* fm1 = m1()->fcl_model();
	FclModel* fm2 = m2()->fcl_model();
	for (int i = 0; i < _num_of_threads; ++i)
	{
		LOG_TRACE("Preparing thread #%i\n", i);
		thread_params_t* params = &all_params[i];
		params->thread_id = i;
		params->result_object = &res;
		//params->collision_manager = this;
		params->fm1 = fm1;
		params->fm2 = fm2;
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

	res.write_to_file(output_filename.c_str());
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

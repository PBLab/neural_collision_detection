#include "program.hpp"
#include "exception.hpp"
#include "trace.hpp"
#include <stdio.h>



int main(int argc, char* argv[])
{
	LOG_INFO("====  ncd start  ====\n");

	try
	{
		Program prog(argc, argv);

		prog.logic();

	}
	catch(const Exception& exp)
	{
		LOG_ERROR("Error: %s\n", exp.msg().c_str());
		return 1;
	}
	catch(...)
	{
		LOG_ERROR("Unknown error running program. Exiting...\n");
		return 1;
	}

	return 0;
}

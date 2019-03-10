#include "trace.hpp"
#include <stdio.h>
#include <time.h>
#include <stdarg.h>


int verbosity = LEVEL_INFO;

void set_verbosity(int verbose)
{
	verbosity = verbose;
}

void color_start(int level)
{
	switch(level)
	{
	case LEVEL_ERROR:
		printf("\033[1;31m");
		break;
	case LEVEL_INFO:
		printf("\033[1;32m");
		break;
	case LEVEL_TRACE:
		printf("\033[37m");
		break;
	case LEVEL_DEBUG:
		printf("\033[36m");
		break;
	};
}

void color_end(int level)
{
	printf("\033[0m");
}


void log(int level, const char * const format, ...)
{
	va_list arg;
	char user_buff[2048];
	char time_buff[32];
	struct tm *str_time;
	time_t now;

	if (level > verbosity)
		return;

	color_start(level);
	now = time(NULL);
	str_time = gmtime(&now);

	strftime(time_buff, sizeof(time_buff), "%Y-%m-%d %H:%M:%S", str_time);

	va_start(arg, format);
	vsnprintf(user_buff, sizeof(user_buff), format, arg);
	va_end(arg);

	printf("[%s]\t%s", time_buff, user_buff);
	color_end(level);
}


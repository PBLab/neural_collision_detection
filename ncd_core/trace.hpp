#pragma once

void set_verbosity(int verbose);
void log(int level, const char * const format, ...);

enum LOG_LEVEL
{
	LEVEL_ERROR = 0,
	LEVEL_INFO,
	LEVEL_TRACE,
	LEVEL_DEBUG,
};

#define LOG_ERROR(msg, ...)	log(LEVEL_ERROR, msg, ##__VA_ARGS__)
#define LOG_INFO(msg, ...) 	log(LEVEL_INFO, msg, ##__VA_ARGS__)
#define LOG_TRACE(msg, ...)	log(LEVEL_TRACE, msg, ##__VA_ARGS__)
#define LOG_DEBUG(msg, ...)	log(LEVEL_DEBUG, msg, ##__VA_ARGS__)

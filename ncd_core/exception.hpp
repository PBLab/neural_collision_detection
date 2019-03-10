#pragma once

#include <string>

class Exception
{
public:
	Exception(const std::string& msg):_msg(msg) {}
	const std::string msg() const {return _msg;}

	std::string _msg;
};

#include "bounding_box.hpp"

bool BoundingBox::contains(float x, float y, float z) const
{
	if (x < min_x || x > max_x)
		return false;
	if (y < min_y || y > max_y)
		return false;
	if (z < min_z || z > max_z)
		return false;
	return true;
}

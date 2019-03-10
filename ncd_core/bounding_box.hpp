#pragma once


class BoundingBox
{
public:
	BoundingBox() {}
	~BoundingBox() {}

	bool contains(float x, float y, float z) const;
	float min_x;
	float max_x;
	float min_y;
	float max_y;
	float min_z;
	float max_z;
};

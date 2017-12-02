#pragma once

#include "model.hpp"

typedef std::vector<Vec3f> PointsVector;

class Collision
{
public:
	static int check_a_collision(const FclModel* fm1, const FclModel* fm2, int x_translation, int y_translation, int z_translation, int x_rot, int y_rot, int z_rot, int num_of_col, PointsVector * collisions);
	static NativeMatrix calc_native_matrix(double x_rot, double y_rot, double z_rot);
private:
	static Matrix3f calc_matrix(double x_rot, double y_rot, double z_rot);
	static double angle_to_rad(double angle);
};


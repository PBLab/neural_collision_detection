#include "collision.hpp"
#include <pthread.h>



int Collision::check_a_collision(FclModelCPtr fm1, FclModelCPtr fm2, int x_translation, int y_translation, int z_translation, int x_rot, int y_rot, int z_rot, int num_of_col, PointsVector *collisions)
{
	Transform3f tf1 = Transform3<float>::Identity();
	Transform3f tf2 = Transform3<float>::Identity();
	Matrix3f m = calc_matrix(x_rot, y_rot, z_rot);
	tf2.linear() = m;
	tf2.translation() = Vec3f(x_translation, y_translation, z_translation);

	bool should_get_collisions = (collisions != NULL);
	CollisionRequest<float> req(num_of_col, should_get_collisions);
	CollisionResult<float> res;

	int num_contacts = collide(&*fm1, tf1, &*fm2, tf2, req, res);
	if (!should_get_collisions)
		return num_contacts;

	for(int i = 0; i < num_contacts; ++i)
	{
		Contact<float> c = res.getContact(i);
		collisions->push_back(c.pos);
	}


	return num_contacts;
}

double Collision::angle_to_rad(double angle)
{
	static const double PI = 3.1415926;
	return angle * PI / 180;
}

NativeMatrix Collision::calc_native_matrix(double x_rot, double y_rot, double z_rot)
{
	NativeMatrix res = {0};
	Matrix3f m = calc_matrix(x_rot, y_rot, z_rot);
	res.values[0][0] = m(0, 0);
	res.values[0][1] = m(0, 1);
	res.values[0][2] = m(0, 2);
	res.values[1][0] = m(1, 0);
	res.values[1][1] = m(1, 1);
	res.values[1][2] = m(1, 2);
	res.values[2][0] = m(2, 0);
	res.values[2][1] = m(2, 1);
	res.values[2][2] = m(2, 2);

	return res;
}

Matrix3f Collision::calc_matrix(double x_rot, double y_rot, double z_rot)
{
	x_rot = angle_to_rad(x_rot);
	y_rot = angle_to_rad(y_rot);
	z_rot = angle_to_rad(z_rot);

	double cos_x = cos(x_rot);
	double sin_x = sin(x_rot);

	double cos_y = cos(y_rot);
	double sin_y = sin(y_rot);

	double cos_z = cos(z_rot);
	double sin_z = sin(z_rot);

	Matrix3f m_x;
	m_x << 1, 0, 0,
		   0, cos_x, -1 * sin_x,
		   0, sin_x, cos_x;

	Matrix3f m_y;
	m_y << cos_y, 0, sin_y,
		   0, 1, 0,
		   -1 * sin_y, 0, cos_y;

	Matrix3f m_z;
	m_z << cos_z, -1 * sin_z, 0,
		   sin_z, cos_z, 0,
		   0, 0, 1;

	Matrix3f m = m_x * m_y * m_z;;

	return m;
}

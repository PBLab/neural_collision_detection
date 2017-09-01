#include "collision.hpp"
#include <pthread.h>



int Collision::check_a_collision(const FclModel* fm1, const FclModel* fm2, int x_translation, int y_translation, int z_translation, int x_rot, int y_rot, int z_rot, int num_of_col)
{
	Transform3f tf1 = Transform3<float>::Identity();
	Transform3f tf2 = Transform3<float>::Identity();
	Matrix3f m = calc_matrix(x_rot, y_rot, z_rot);
	tf2.linear() = m;
	//tf2.linear().setIdentity();
	tf2.translation() = Vec3f(x_translation, y_translation, z_translation);

	CollisionRequest<float> req(num_of_col, false);
	CollisionResult<float> res;

	int num_contacts = collide(fm1, tf1, fm2, tf2, req, res);
	return num_contacts;
}

double Collision::angle_to_rad(double angle)
{
	static const double PI = 3.1415926;
	return angle * PI / 180;
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
	//m << 1, 0, 0, 0, 1, 0, 0, 0, 1;

	return m;
}

// void print_contact(Contact<float>& contact, int idx)
// {
// 	LOG_DEBUG("Contact #%i: (%f, %f, %f), b1 = %i, b2 = %i, depth: %f\n", idx, contact.pos[0], contact.pos[1], contact.pos[2], contact.b1, contact.b2, contact.penetration_depth);
// }
// 
// void parse_contacts(CollisionResult<float>& res, int num_contacts)
// {
// 	std::vector<Contact<float>> contacts;
// 	res.getContacts(contacts);
// 	
// 	for (int i = 0; i < num_contacts; ++i)
// 	{
// 		print_contact(contacts[i], i);
// 	}
// 
// }

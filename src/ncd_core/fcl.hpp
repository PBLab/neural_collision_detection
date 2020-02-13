#pragma once

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#include "fcl/geometry/bvh/BVH_model.h"
#include "fcl/math/bv/OBBRSS.h"
#include "fcl/math/bv/AABB.h"
#include "fcl/narrowphase/collision.h"
#include "fcl/common/types.h"
#include <vector>
#pragma GCC diagnostic pop

using namespace fcl;
using namespace std;
typedef OBBRSS<int> OBBRSS_;
typedef BVHModel< OBBRSS<float> > FclModel;
//typedef BVHModel< AABB<float> > FclModel;
typedef Vector3<float> Vec3f;
typedef struct NativeMatrix {float values[3][3];} NativeMatrix;

/*

    Rotation Constant Axis Class
    This class is an interface to generate a rotation trajectory in the
   cartesian space

    Copyright 2019-2020 Università della Campania Luigi Vanvitelli

    Author: Marco Costanzo <marco.costanzo@unicampania.it>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

#include "sun_traj_lib/Rotation_Const_Axis_Traj.h"

using namespace TooN;
using namespace std;

namespace sun
{
/*======CONSTRUCTORS=========*/

/*
    Constructor with total time as input
*/
Rotation_Const_Axis_Traj::Rotation_Const_Axis_Traj(const UnitQuaternion &initial_quat, const Vector<3> &axis,
                                                   const Scalar_Traj_Interface &traj_theta)
  : Quaternion_Traj_Interface(NAN, NAN), _initial_quat(initial_quat), _axis(unit(axis)), _traj_theta(traj_theta.clone())
{
  if (norm(axis) < 10.0 * std::numeric_limits<double>::epsilon())
  {
    cout << TRAJ_WARN_COLOR "[Rotation_Const_Axis_Traj] WARNING: axis is zero -> no rotation" CRESET << endl;
    _axis = Zeros;
  }
}

Rotation_Const_Axis_Traj::Rotation_Const_Axis_Traj(const UnitQuaternion &initial_quat, const UnitQuaternion &final_quat,
                                                   const Scalar_Traj_Interface &traj_theta, double &angle)
  : Quaternion_Traj_Interface(NAN, NAN), _initial_quat(initial_quat), _traj_theta(traj_theta.clone())
{
  UnitQuaternion Delta_Q = final_quat * inv(initial_quat);
  sun::AngVec Delta_angvec = Delta_Q.toangvec();
  _axis = Delta_angvec.getVec();
  angle = Delta_angvec.getAng();
  if (norm(_axis) < 10.0 * std::numeric_limits<double>::epsilon())
  {
    cout << TRAJ_WARN_COLOR "[Rotation_Const_Axis_Traj] WARNING: axis is zero -> no rotation" CRESET << endl;
    _axis = Zeros;
  }
}

Rotation_Const_Axis_Traj::Rotation_Const_Axis_Traj(const Rotation_Const_Axis_Traj &traj)
  : Quaternion_Traj_Interface(NAN, NAN)
{
  _initial_quat = traj._initial_quat;
  _axis = traj._axis;
  _traj_theta = Scalar_Traj_Interface_Ptr(traj._traj_theta->clone());
}

/*
    Clone the object in the heap
*/
Rotation_Const_Axis_Traj *Rotation_Const_Axis_Traj::clone() const
{
  return new Rotation_Const_Axis_Traj(*this);
}

/*======END CONSTRUCTORS=========*/

/*====== GETTERS =========*/

/*
    Get rotation axis
*/
Vector<3> Rotation_Const_Axis_Traj::getAxis() const
{
  return _axis;
}

/*
    Get initial quaternion
*/
UnitQuaternion Rotation_Const_Axis_Traj::getInitialQuat() const
{
  return _initial_quat;
}

/*
    Get the final time instant
*/
double Rotation_Const_Axis_Traj::getFinalTime() const
{
  return _traj_theta->getFinalTime();
}

/*
    Get the initial time instant
*/
double Rotation_Const_Axis_Traj::getInitialTime() const
{
  return _traj_theta->getInitialTime();
}

/*====== END GETTERS =========*/

/*====== SETTERS =========*/

/*
    Set rotation axis
*/
void Rotation_Const_Axis_Traj::setAxis(const Vector<3> &axis)
{
  _axis = unit(axis);
  if (norm(axis) < 10.0 * std::numeric_limits<double>::epsilon())
  {
    cout << TRAJ_WARN_COLOR "axis is zero -> no rotation" CRESET << endl;
    _axis = Zeros;
  }
}

/*
    Set initial quaternion
*/
void Rotation_Const_Axis_Traj::setInitialQuat(const UnitQuaternion &initial_quat)
{
  _initial_quat = initial_quat;
}

/*
    Change the initial time instant (translate the trajectory in the time)
*/
void Rotation_Const_Axis_Traj::changeInitialTime(double initial_time)
{
  _traj_theta->changeInitialTime(initial_time);
}

/*
    Trajectory for the angle variable should be a traj from theta_i to theta_f
    i.e. from the initial angle to the final angle
*/
void Rotation_Const_Axis_Traj::setScalarTraj(const Scalar_Traj_Interface &traj_theta)
{
  _traj_theta = Scalar_Traj_Interface_Ptr(traj_theta.clone());
}

/*====== END SETTERS =========*/

/*====== TRANSFORM =========*/

/*
    Change the reference frame of the trajectory
    Apply a rotation matrix to the trajectory
    new_R_curr is the rotation matrix of the current frame w.r.t. the new frame
*/
void Rotation_Const_Axis_Traj::changeFrame(const Matrix<3, 3> &new_R_curr)
{
  changeFrame(UnitQuaternion(new_R_curr));
}

/*
    Change the reference frame of the trajectory
    Apply a rotation matrix to the trajectory
    new_Q_curr is the Quaterion representing the rotation matrix of the current
   frame w.r.t. the new frame
*/
void Rotation_Const_Axis_Traj::changeFrame(const UnitQuaternion &new_Q_curr)
{
  _initial_quat = new_Q_curr * _initial_quat;
  _axis = new_Q_curr * _axis;
}

/*====== END TRANSFORM =========*/

/*
    Get Delta quaterinion, i.e. initial_Q_now
*/
UnitQuaternion Rotation_Const_Axis_Traj::getDeltaQuat(double secs) const
{
  if (_axis[0] == 0.0 && _axis[1] == 0.0 && _axis[2] == 0.0)
  {
    return UnitQuaternion();
  }
  else
  {
    return UnitQuaternion::angvec(_traj_theta->getPosition(secs), _axis);
  }
}

/*
     Get Quaternion at time secs
*/
UnitQuaternion Rotation_Const_Axis_Traj::getQuaternion(double secs) const
{
  return getDeltaQuat(secs) * _initial_quat;
}

/*
    Get Angular Velocity at time secs
*/
Vector<3> Rotation_Const_Axis_Traj::getVelocity(double secs) const
{
  return _traj_theta->getVelocity(secs) * _axis;
}

/*
    Get Angular Acceleration at time secs
*/
Vector<3> Rotation_Const_Axis_Traj::getAcceleration(double secs) const
{
  return _traj_theta->getAcceleration(secs) * _axis;
}

}  // namespace sun

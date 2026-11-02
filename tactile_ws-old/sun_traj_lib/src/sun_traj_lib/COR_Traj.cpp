/*

    Rotation about a center of rotation - Trajectory Generator Class
    This class is an interface to generate arbitrary cartesian trajectory in the
   cartesian space
    the angular position is giver as UnitQuaternion

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

#include "sun_traj_lib/COR_Traj.h"

using namespace TooN;
using namespace std;

namespace sun
{
/*
    Constructor
*/
COR_Traj::COR_Traj(const Vector<3> &COR, const Vector<3> &normal, const Vector<3> &pi,
                   const UnitQuaternion &initial_quat, const Scalar_Traj_Interface &traj_theta)
  : Cartesian_Traj_Interface(NAN, NAN), _initial_quat(initial_quat), _pos_traj(normal, COR, pi, traj_theta)
{
  if (_pos_traj.isAPoint())
  {
    if (norm(normal) < 10.0 * std::numeric_limits<double>::epsilon())
    {
      cout << TRAJ_WARN_COLOR "[COR_Traj] WARNING: axis is zero -> no rotation" CRESET << endl;
      _rot_axis = Zeros;
    }
    else
    {
      _rot_axis = unit(normal);
    }
  }
  else
  {
    _rot_axis = _pos_traj.getOrientation()[2];
  }
}

COR_Traj::COR_Traj(const UnitQuaternion &initial_quat, const Position_Circumference_Traj &circ_traj)
  : Cartesian_Traj_Interface(NAN, NAN), _initial_quat(initial_quat), _pos_traj(circ_traj)
{
  if (_pos_traj.isAPoint())
  {
    _rot_axis = Zeros;
  }
  else
  {
    _rot_axis = _pos_traj.getOrientation()[2];
  }
}

/*
    Clone the object in the heap
*/
COR_Traj *COR_Traj::clone() const
{
  return new COR_Traj(*this);
}

/*======END CONSTRUCTORS=========*/

/*====== GETTERS =========*/

/*
    Get the final time instant
*/
double COR_Traj::getFinalTime() const
{
  return _pos_traj.getFinalTime();
}

/*
    Get the initial time instant
*/
double COR_Traj::getInitialTime() const
{
  return _pos_traj.getInitialTime();
}

/*====== END GETTERS =========*/

/*====== SETTERS =========*/

/*
    Change the initial time instant (translate the trajectory in the time)
*/
void COR_Traj::changeInitialTime(double initial_time)
{
  _pos_traj.changeInitialTime(initial_time);
}

/*====== END SETTERS =========*/

/*====== TRANSFORM =========*/

/*====== END TRANSFORM =========*/

/*
    Get Delta quaterinion, i.e. initial_Q_now
*/
UnitQuaternion COR_Traj::getDeltaQuat(double secs) const
{
  if (_rot_axis[0] == 0.0 && _rot_axis[1] == 0.0 && _rot_axis[2] == 0.0)
  {
    return UnitQuaternion();
  }
  else
  {
    return UnitQuaternion::angvec(_pos_traj.getAngularPosition(secs), _rot_axis);
  }
}

/*
    Get Position at time secs
*/
Vector<3> COR_Traj::getPosition(double secs) const
{
  return _pos_traj.getPosition(secs);
}

/*
    Get Quaternion at time secs
*/
UnitQuaternion COR_Traj::getQuaternion(double secs) const
{
  return getDeltaQuat(secs) * _initial_quat;
}

/*
    Get Linear Velocity at time secs
*/
Vector<3> COR_Traj::getLinearVelocity(double secs) const
{
  return _pos_traj.getVelocity(secs);
}

/*
    Get Angular Velocity at time secs
*/
Vector<3> COR_Traj::getAngularVelocity(double secs) const
{
  return _pos_traj.getAngularVelocity(secs) * _rot_axis;
}

}  // namespace sun
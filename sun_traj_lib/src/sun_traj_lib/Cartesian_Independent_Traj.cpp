/*

    Cartesian Trajectory Generator Class
    This class is an interface to generate arbitrary cartesian trajectory in the
   cartesian space
    the angular position is giver as UnitQuaterion

    Copyright 2018-2020 Università della Campania Luigi Vanvitelli

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

#include "sun_traj_lib/Cartesian_Independent_Traj.h"

using namespace TooN;

namespace sun
{
/*======CONSTRUCTORS=========*/

/*
    Constructor
*/
Cartesian_Independent_Traj::Cartesian_Independent_Traj(const Position_Traj_Interface &pos_traj,
                                                       const Quaternion_Traj_Interface &quat_traj)
  : Cartesian_Traj_Interface(NAN, NAN), _pos_traj(pos_traj.clone()), _quat_traj(quat_traj.clone())
{
}

/*
    Copy Constructor
*/
Cartesian_Independent_Traj::Cartesian_Independent_Traj(const Cartesian_Independent_Traj &traj)
  : Cartesian_Traj_Interface(NAN, NAN), _pos_traj(traj._pos_traj->clone()), _quat_traj(traj._quat_traj->clone())
{
}

/*
    Clone the object in the heap
*/
Cartesian_Independent_Traj *Cartesian_Independent_Traj::clone() const
{
  return new Cartesian_Independent_Traj(*this);
}

/*======END CONSTRUCTORS=========*/

/*====== GETTERS =========*/

/*
    Get the final time instant
*/
double Cartesian_Independent_Traj::getFinalTime() const
{
  double final_time_pos = _pos_traj->getFinalTime();
  double final_time_quat = _quat_traj->getFinalTime();
  if (final_time_pos >= final_time_quat)
    return final_time_pos;
  else
    return final_time_quat;
}

/*
    Get the initial time instant
*/
double Cartesian_Independent_Traj::getInitialTime() const
{
  double initial_time_pos = _pos_traj->getInitialTime();
  double initial_time_quat = _quat_traj->getInitialTime();
  if (initial_time_pos <= initial_time_quat)
    return initial_time_pos;
  else
    return initial_time_quat;
}

/*
    Get the duration [from base class]
*/
// double getDuration() const;

/*
    Get the time left [from base class]
*/
// double getTimeLeft(double secs) const;

/*====== END GETTERS =========*/

/*====== SETTERS =========*/

/*
    Change the initial time instant (translate the trajectory in the time)
*/
void Cartesian_Independent_Traj::changeInitialTime(double initial_time)
{
  double previous_initial_time = getInitialTime();
  double Delta_T = previous_initial_time - initial_time;
  _pos_traj->changeInitialTime(_pos_traj->getInitialTime() - Delta_T);
  _quat_traj->changeInitialTime(_quat_traj->getInitialTime() - Delta_T);
}

/*====== END SETTERS =========*/

/*====== TRANSFORM =========*/

/*
    Change the reference frame of the trajectory
    Apply an homogeneous transfrmation matrix to the trajectory
    new_T_curr is the homog transf matrix of the current frame w.r.t. the new
   frame
*/
void Cartesian_Independent_Traj::changeFrame(const Matrix<4, 4> &new_T_curr)
{
  _pos_traj->changeFrame(new_T_curr);
  _quat_traj->changeFrame(new_T_curr);
}

/*====== END TRANSFORM =========*/

/*
    return true if the trajectory is compleate at time secs
*/
bool Cartesian_Independent_Traj::isCompleate(double secs) const
{
  if (!_pos_traj->isCompleate(secs))
    return false;
  if (!_quat_traj->isCompleate(secs))
    return false;
  return true;
}

/*
    return true if the trajectory is started at time secs
*/
bool Cartesian_Independent_Traj::isStarted(double secs) const
{
  if (_pos_traj->isStarted(secs))
    return true;
  if (_quat_traj->isStarted(secs))
    return true;
  return false;
}

/*
    Get Position at time secs
*/
Vector<3> Cartesian_Independent_Traj::getPosition(double secs) const
{
  return _pos_traj->getPosition(secs);
}

/*
    Get Quaternion at time secs
*/
UnitQuaternion Cartesian_Independent_Traj::getQuaternion(double secs) const
{
  return _quat_traj->getQuaternion(secs);
}

/*
    Get Linear Velocity at time secs
*/
Vector<3> Cartesian_Independent_Traj::getLinearVelocity(double secs) const
{
  return _pos_traj->getVelocity(secs);
}

/*
    Get Angular Velocity at time secs
*/
Vector<3> Cartesian_Independent_Traj::getAngularVelocity(double secs) const
{
  return _quat_traj->getVelocity(secs);
}

/*
    Get Twist Velocity at time secs [ v , w ]^T
    [from base class]
*/
// Vector<6> getTwist(double secs) const ;

}  // namespace sun
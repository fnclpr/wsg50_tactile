/*

    Trapez Generator Class
    This class generates a scalar trajectory w. a vel trapez profile

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

#include "sun_traj_lib/Trapez_Vel_Traj.h"

using namespace std;

namespace sun
{
/*=======CONSTRUCTORS======*/

/*
    Constructor
*/
Trapez_Vel_Traj::Trapez_Vel_Traj(

    double cruise_speed, double cruise_duration, double acceleration, double initial_position, double initial_time)
  : Scalar_Traj_Interface(2.0 * (cruise_speed / acceleration) + cruise_duration, initial_time)
  , _pi(initial_position)
  , _ddp(acceleration)
  , _tc(cruise_speed / acceleration)
  , _tv(cruise_duration)
{
  if (acceleration == 0.0 && cruise_speed == 0.0)
  {
    // zero movment
    _tc = 0.0;
  }

  if (isnan(_tc) || _tc < 0.0 || _tv < 0.0)
  {
    cout << TRAJ_ERROR_COLOR "ERROR in Trapez_Vel_Traj() | non valid time" CRESET << endl;
    exit(-1);
  }
}

/*
    Clone the object in the heap
*/
Trapez_Vel_Traj *Trapez_Vel_Traj::clone() const
{
  return new Trapez_Vel_Traj(*this);
}

/*=======END CONSTRUCTORS======*/

/*======= GETTERS =========*/

double Trapez_Vel_Traj::getFinalPosition() const
{
  return _pi + _ddp * _tc * _tv + _ddp * pow(_tc, 2);
}

double Trapez_Vel_Traj::getCruiseTime() const
{
  return _tc;
}

/*======= END GETTERS =========*/

/*======SETTERS==========*/

/*======END SETTERS==========*/

/*
    Get Position at time secs
*/
double Trapez_Vel_Traj::getPosition(double secs) const
{
  double t = secs - _initial_time;

  if (t < 0.0)
  {
    return _pi;
  }
  if (t <= _tc)
  {
    return _pi + 0.5 * _ddp * pow(t, 2);
  }
  if (t <= (_tc + _tv))
  {
    return _pi + _ddp * _tc * (t - 0.5 * _tc);
  }
  if (t <= (2.0 * _tc + _tv))
  {
    return _pi - 0.5 * _ddp * pow(_tc, 2) + _ddp * _tc * t - 0.5 * _ddp * pow(t - _tc - _tv, 2);
  }
  else
  {
    return getFinalPosition();
  }
}

/*
    Get Velocity at time secs
*/
double Trapez_Vel_Traj::getVelocity(double secs) const
{
  double t = secs - _initial_time;

  if (t < 0.0)
  {
    return 0.0;
  }
  if (t <= _tc)
  {
    return _ddp * t;
  }
  if (t <= (_tc + _tv))
  {
    return _ddp * _tc;
  }
  if (t <= (2.0 * _tc + _tv))
  {
    return -_ddp * (t - 2.0 * _tc - _tv);
  }
  else
  {
    return 0.0;
  }
}

/*
    Get Acceleration at time secs
*/
double Trapez_Vel_Traj::getAcceleration(double secs) const
{
  double t = secs - _initial_time;

  if (t < 0.0)
  {
    return 0.0;
  }
  if (t <= _tc)
  {
    return _ddp;
  }
  if (t <= (_tc + _tv))
  {
    return 0.0;
  }
  if (t <= (2.0 * _tc + _tv))
  {
    return -_ddp;
  }
  else
  {
    return 0.0;
  }
}

}  // namespace sun

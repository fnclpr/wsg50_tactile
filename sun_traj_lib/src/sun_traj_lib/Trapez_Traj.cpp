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

#include "sun_traj_lib/Trapez_Traj.h"

using namespace std;

namespace sun
{
/*=======CONSTRUCTORS======*/

bool Trapez_Traj::checkTrapez(double duration, double initial_position, double final_position, double cruise_speed)
{
  if (((fabs(final_position - initial_position) / duration) >= fabs(cruise_speed)) ||
      (fabs(cruise_speed) > (2.0 * (fabs(final_position - initial_position) / duration))) ||
      (((final_position - initial_position) * cruise_speed) < 0.0))
  {
    cout << fabs(final_position - initial_position) / duration << endl;
    cout << fabs(cruise_speed) << endl;
    cout << (2.0 * (fabs(final_position - initial_position) / duration)) << endl;
    return false;
  }
  return true;
}

/*
    Constructor
*/
Trapez_Traj::Trapez_Traj(double duration, double initial_position, double final_position, double cruise_speed,
                         double initial_time)
  : Scalar_Traj_Interface(duration, initial_time), _pi(initial_position), _pf(final_position)
{
  if (((fabs(_pf - _pi) / getDuration()) >= fabs(cruise_speed)) ||
      (fabs(cruise_speed) > (2.0 * (fabs(_pf - _pi) / getDuration()))) || (((_pf - _pi) * cruise_speed) < 0.0))
  {
    cout << fabs(_pf - _pi) / getDuration() << endl;
    cout << fabs(cruise_speed) << endl;
    cout << (2.0 * (fabs(_pf - _pi) / getDuration())) << endl;
    cout << TRAJ_ERROR_COLOR "ERROR in Trapez_Traj()" CRESET << endl;
    exit(-1);
  }

  _tc = (_pi - _pf + cruise_speed * getDuration()) / cruise_speed;

  _ddp = cruise_speed / _tc;
}

/*
    Clone the object in the heap
*/
Trapez_Traj *Trapez_Traj::clone() const
{
  return new Trapez_Traj(*this);
}

/*=======END CONSTRUCTORS======*/

/*======= GETTERS =========*/

/*======= END GETTERS =========*/

/*======SETTERS==========*/

/*======END SETTERS==========*/

/*
    Get Position at time secs
*/
double Trapez_Traj::getPosition(double secs) const
{
  double t = secs - _initial_time;
  if (t < 0.0)
  {
    return _pi;
  }
  if (t <= _tc)
  {
    return (_pi + 0.5 * _ddp * pow(t, 2));
  }
  if (t <= (getDuration() - _tc))
  {
    return (_pi + _ddp * _tc * (t - (_tc / 2.0)));
  }
  if (t <= getDuration())
  {
    return (_pf - 0.5 * _ddp * pow(getDuration() - t, 2));
  }
  else
  {
    return (_pf);
  }
}

/*
    Get Velocity at time secs
*/
double Trapez_Traj::getVelocity(double secs) const
{
  double t = secs - _initial_time;
  if (t < 0.0)
  {
    return 0.0;
  }
  if (t <= _tc)
  {
    return (_ddp * t);
  }
  if (t <= (getDuration() - _tc))
  {
    return (_ddp * _tc);
  }
  if (t <= getDuration())
  {
    return (_ddp * (getDuration() - t));
  }
  else
  {
    return (0.0);
  }
}

/*
    Get Acceleration at time secs
*/
double Trapez_Traj::getAcceleration(double secs) const
{
  double t = secs - _initial_time;
  if (t < 0.0)
  {
    return 0.0;
  }
  if (t <= _tc)
  {
    return (_ddp);
  }
  if (t <= (getDuration() - _tc))
  {
    return (0.0);
  }
  if (t <= getDuration())
  {
    return (-_ddp);
  }
  else
  {
    return (0.0);
  }
}

}  // namespace sun
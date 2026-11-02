/*

    Sine Generator Class
    This class generates a scalar trajectory w. sine wave

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

#include "sun_traj_lib/Sine_Traj.h"
#define _USE_MATH_DEFINES
#include <cmath>

using namespace std;

namespace sun
{
/*=======CONSTRUCTORS======*/

/*
    Constructor
*/
Sine_Traj::Sine_Traj(double duration, double amplitude, double frequency, double bias, double phase,
                     double initial_time)
  : Scalar_Traj_Interface(duration, initial_time)
  , _A(amplitude)
  , _pulse(2.0 * M_PI * frequency)
  , _bias(bias)
  , _phi(phase)
{
}

/*
    Clone the object in the heap
*/
Sine_Traj *Sine_Traj::clone() const
{
  return new Sine_Traj(*this);
}

/*=======END CONSTRUCTORS======*/

/*======= GETTERS =========*/

/*======= END GETTERS =========*/

/*======SETTERS==========*/

/*======END SETTERS==========*/

/*
    Get Position at time secs
*/
double Sine_Traj::getPosition(double secs) const
{
  double _time = secs;
  if (_time < _initial_time)
  {
    _time = _initial_time;
  }
  if (_time > _final_time)
  {
    _time = _final_time;
  }
  _time = _time - _initial_time;
  return _A * sin(_pulse * _time + _phi) + _bias;
}

/*
    Get Velocity at time secs
*/
double Sine_Traj::getVelocity(double secs) const
{
  double _time = secs;
  if (_time < _initial_time)
  {
    _time = _initial_time;
  }
  if (_time > _final_time)
  {
    _time = _final_time;
  }
  _time = _time - _initial_time;
  return _pulse * _A * cos(_pulse * _time + _phi);
}

/*
    Get Acceleration at time secs
*/
double Sine_Traj::getAcceleration(double secs) const
{
  double _time = secs;
  if (_time < _initial_time)
  {
    _time = _initial_time;
  }
  if (_time > _final_time)
  {
    _time = _final_time;
  }
  _time = _time - _initial_time;
  return -pow(_pulse, 2) * _A * sin(_pulse * _time + _phi);
}

}  // namespace sun

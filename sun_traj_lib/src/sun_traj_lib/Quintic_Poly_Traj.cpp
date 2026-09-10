/*

    Quintic Poly Generator Class
    This class generates a scalar trajectory w. a quintic poly

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

#include "sun_traj_lib/Quintic_Poly_Traj.h"

using namespace TooN;
using namespace std;

namespace sun
{
/*=======CONSTRUCTORS======*/

/*
    Constructor
*/
Quintic_Poly_Traj::Quintic_Poly_Traj(double duration, double initial_position, double final_position,
                                     double initial_time, double initial_velocity, double final_velocity,
                                     double initial_acceleration, double final_acceleration)
  : Scalar_Traj_Interface(duration, initial_time)
  , _pi(initial_position)
  , _pf(final_position)
  , _vi(initial_velocity)
  , _vf(final_velocity)
  , _aci(initial_acceleration)
  , _acf(final_acceleration)
{
  updateCoefficients();
}

/*
    Clone the object in the heap
*/
Quintic_Poly_Traj *Quintic_Poly_Traj::clone() const
{
  return new Quintic_Poly_Traj(*this);
}

/*=======END CONSTRUCTORS======*/

/*======= GETTERS =========*/

double Quintic_Poly_Traj::getInitialPosition() const
{
  return _pi;
}

double Quintic_Poly_Traj::getFinalPosition() const
{
  return _pf;
}

double Quintic_Poly_Traj::getInitialVelocity() const
{
  return _vi;
}

double Quintic_Poly_Traj::getFinalVelocity() const
{
  return _vf;
}

double Quintic_Poly_Traj::getInitialAcceleration() const
{
  return _aci;
}

double Quintic_Poly_Traj::getFinalAcceleration() const
{
  return _acf;
}

/*======= END GETTERS =========*/

/*======SETTERS==========*/

void Quintic_Poly_Traj::setInitialPosition(double pi)
{
  _pi = pi;
  updateCoefficients();
}

void Quintic_Poly_Traj::setFinalPosition(double pf)
{
  _pf = pf;
  updateCoefficients();
}

void Quintic_Poly_Traj::setInitialVelocity(double vi)
{
  _vi = vi;
  updateCoefficients();
}

void Quintic_Poly_Traj::setFinalVelocity(double vf)
{
  _vf = vf;
  updateCoefficients();
}

void Quintic_Poly_Traj::setInitialAcceleration(double ai)
{
  _aci = ai;
  updateCoefficients();
}

void Quintic_Poly_Traj::setFinalAcceleration(double af)
{
  _acf = af;
  updateCoefficients();
}

/*
    Change the initial time instant (translate the trajectory)
*/
void Quintic_Poly_Traj::changeInitialTime(double initial_time)
{
  Traj_Generator_Interface::changeInitialTime(initial_time);
  updateCoefficients();
}

/*======END SETTERS==========*/

/*
    Get Position at time secs
*/
double Quintic_Poly_Traj::getPosition(double secs) const
{
  if (secs < _initial_time)
  {
    return _pi;
  }
  if (secs > _final_time)
  {
    return _pf;
  }
  return polyval(_poly_coeff, secs - _initial_time);
}

/*
    Get Velocity at time secs
*/
double Quintic_Poly_Traj::getVelocity(double secs) const
{
  if (secs < _initial_time)
  {
    return 0.0;
  }
  if (secs > _final_time)
  {
    return 0.0;
  }
  return polyval(_vel_poly_coeff, secs - _initial_time);
}

/*
    Get Acceleration at time secs
*/
double Quintic_Poly_Traj::getAcceleration(double secs) const
{
  if (secs < _initial_time)
  {
    return 0.0;
  }
  if (secs > _final_time)
  {
    return 0.0;
  }
  return polyval(_acc_poly_coeff, secs - _initial_time);
}

/*
    Update poly coefficients
*/
void Quintic_Poly_Traj::updateCoefficients()
{
  // This is the effective total time of motion
  double t = getDuration();

  if (t < 10.0 * std::numeric_limits<double>::epsilon())
  {
    cout << TRAJ_WARN_COLOR "[Quintic_Poly_Traj] WARNING: duration is zero... "
                            "I will fix this..." CRESET
         << endl;
    t = QUINTIC_POLY_EPS_TIME;
  }

  // These coefficients are known
  _poly_coeff[5] = _pi;
  _poly_coeff[4] = _vi;
  _poly_coeff[3] = _aci / 2.0;

  // Prepare pow
  double t_2 = pow(t, 2);
  double t_3 = pow(t, 3);
  double t_4 = pow(t, 4);
  double t_5 = pow(t, 5);

  // Construct inverse of A ( A*poly_coeff = B )
  Matrix<3, 3> A_inv = Data(6.0 / t_5, -3.0 / t_4, 1.0 / (2.0 * t_3), -15.0 / t_4, 7.0 / t_3, -1.0 / t_2, 10.0 / t_3,
                            -4.0 / t_2, 1.0 / (2.0 * t));
  // Construct B
  Vector<3> B = makeVector(_pf - _pi - _vi * t - (_aci / 2.0) * t_2, _vf - _vi - _aci * t, _acf - _aci);

  // Calculate poly coeff
  _poly_coeff.slice<0, 3>() = A_inv * B;

  // calculate coeff of dp and ddp as polydiff
  _vel_poly_coeff = polydiff(_poly_coeff);
  _acc_poly_coeff = polydiff(_vel_poly_coeff);
}

}  // namespace sun
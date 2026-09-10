/*

    Position Circumference Trajectory Generator Class
    This class is generates a circumference trajectory in the cartesian space

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

#include "sun_traj_lib/Position_Circumference_Traj.h"

using namespace std;
using namespace TooN;

namespace sun
{
/*======CONSTRUCTORS========*/

/*
    Full Constructor
*/
Position_Circumference_Traj::Position_Circumference_Traj(const Vector<3> &r_hat, const Vector<3> &d,
                                                         const Vector<3> &pi, const Scalar_Traj_Interface &traj_s)
  : Position_Traj_Interface(NAN, NAN), _traj_s(traj_s.clone())
{
  Vector<3> _r_hat = unit(r_hat);

  Vector<3> delta = pi - d;

  if (fabs(delta * r_hat) >= norm(delta) || (norm(r_hat) < 10.0 * std::numeric_limits<double>::epsilon()))
  {
    cout << TRAJ_WARN_COLOR "THE CIRCUMFERENCE TRAJ IS A POINT!" CRESET << endl;
    _c = pi;
    _R = Identity;
    _rho = 0.0;
    return;
  }

  _c = d + (delta * r_hat) * r_hat;

  _rho = norm(pi - _c);

  _R.T()[0] = unit(pi - _c);
  _R.T()[2] = _r_hat;
  _R.T()[1] = _R.T()[2] ^ _R.T()[0];
}

/*
    Compute the params of the circumference given the start point, the final
   point and radius
    r_hat = normal to the circumference plane
    pi = initial point
    pf = final point
    rho = radius
    c (return param) = center
    angle (return param) = angle to use to generate the scalar trajectory
    sign_plut (optional input) = there are 2 solutions... this bool select the
   solution
*/
void Position_Circumference_Traj::two_points_2_center(const Vector<3> &r_hat, const Vector<3> &pi, const Vector<3> &pf,
                                                      double rho, Vector<3> &c, double &angle, bool sign_plus)
{
  double sign = 1.0;
  if (!sign_plus)
  {
    sign = -1.0;
  }

  Vector<3> _r_hat = unit(r_hat);

  c = ((pf + pi) / 2.0) + sign * sqrt(pow(rho, 2) - pow(norm(pf - pi) / 2.0, 2)) * unit(_r_hat ^ (pf - pi));

  angle = acos((pf - c) * (pi - c) / (norm(pf - c) * norm(pi - c)));
}

/*
    Copy Constructor
*/
Position_Circumference_Traj::Position_Circumference_Traj(const Position_Circumference_Traj &traj)
  : Position_Traj_Interface(traj), _c(traj._c), _rho(traj._rho), _R(traj._R), _traj_s(traj._traj_s->clone())
{
}

/*
    Clone the object in the heap
*/
Position_Circumference_Traj *Position_Circumference_Traj::clone() const
{
  return new Position_Circumference_Traj(*this);
}

/*======END CONSTRUCTORS========*/

/*====== GETTERS ========*/

/*
    Get center of the Circumference
    if the circumferece is a point return The point
*/
Vector<3> Position_Circumference_Traj::getCenter() const
{
  return _c;
}

/*
    Get orientation of the Circumference as Rotation Matrix
    if the circumferece is a point return Identity
*/
Matrix<3, 3> Position_Circumference_Traj::getOrientation() const
{
  return _R;
}

/*
    Get radius of the Circumference
    if the circumferece is a point return 0
*/
double Position_Circumference_Traj::getRadius() const
{
  return _rho;
}

/*
    check if the circumference is a point
*/
bool Position_Circumference_Traj::isAPoint() const
{
  return (_rho == 0.0);
}

/*
    Get the final time instant
*/
double Position_Circumference_Traj::getFinalTime() const
{
  return _traj_s->getFinalTime();
}

/*
    Get the initial time instant
*/
double Position_Circumference_Traj::getInitialTime() const
{
  return _traj_s->getInitialTime();
}

/*====== END GETTERS ========*/

/*====== SETTERS =========*/

/*
    Set the scalar trajectory
    Trajectory for the scalar s variable should be a traj from 0 to final_angle
    s = 0 -> _pi   &   s = 1 -> _pf
    Note: Velocities and accelerations
    TODO!
*/
void Position_Circumference_Traj::setScalarTraj(const Scalar_Traj_Interface &s_traj)
{
  _traj_s = Scalar_Traj_Interface_Ptr(s_traj.clone());
}

/*
    Change the initial time instant (translate the trajectory in the time)
*/
void Position_Circumference_Traj::changeInitialTime(double initial_time)
{
  _traj_s->changeInitialTime(initial_time);
}

/*====== END SETTERS =========*/

/*====== TRANSFORM =========*/

/*
    Change the reference frame of the trajectory
    Apply an homogeneous transfrmation matrix to the trajectory
    new_T_curr is the homog transf matrix of the current frame w.r.t. the new
   frame
*/
void Position_Circumference_Traj::changeFrame(const Matrix<4, 4> &new_T_curr)
{
  Vector<4> tmp_v;
  tmp_v[3] = 1.0;

  tmp_v.slice<0, 3>() = _c;
  _c = (new_T_curr * tmp_v).slice<0, 3>();
  if (!isAPoint())
  {
    _R = new_T_curr.slice<0, 0, 3, 3>() * _R;
  }
}

/*====== END TRANSFORM =========*/

/*====== RUNNERS =========*/

/*
    Get Position at time secs
*/
Vector<3> Position_Circumference_Traj::getPosition(double secs) const
{
  if (isAPoint())
  {
    return _c;
  }

  double s = _traj_s->getPosition(secs);

  return _c + _R * makeVector(_rho * cos(s), _rho * sin(s), 0.0);
}

/*
    Get Velocity at time secs
*/
Vector<3> Position_Circumference_Traj::getVelocity(double secs) const
{
  if (isAPoint())
  {
    return Zeros;
  }

  double s = _traj_s->getPosition(secs);
  double s_dot = _traj_s->getVelocity(secs);

  return _R * makeVector(-_rho * sin(s) * s_dot, _rho * cos(s) * s_dot, 0.0);
}

/*
    Get Acceleration at time secs
*/
Vector<3> Position_Circumference_Traj::getAcceleration(double secs) const
{
  if (isAPoint())
  {
    return Zeros;
  }

  double s = _traj_s->getPosition(secs);
  double s_dot = _traj_s->getVelocity(secs);
  double s_2dot = _traj_s->getAcceleration(secs);

  return _R * makeVector(-_rho * cos(s) * pow(s_dot, 2) - _rho * sin(s) * s_2dot,
                         -_rho * sin(s) * pow(s_dot, 2) + _rho * cos(s) * s_2dot, 0.0);
}

/*
    Get the angular position (position)
*/
double Position_Circumference_Traj::getAngularPosition(double secs) const
{
  return _traj_s->getPosition(secs);
}

/*
    Get the angular velocity
*/
double Position_Circumference_Traj::getAngularVelocity(double secs) const
{
  return _traj_s->getVelocity(secs);
}

/*
    Get the angular velocity
*/
double Position_Circumference_Traj::getAngularAcceleration(double secs) const
{
  return _traj_s->getAcceleration(secs);
}

/*====== END RUNNERS =========*/

}  // namespace sun
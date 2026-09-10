/*

    Position Line Trajectory Generator Class
    This class is generates a line trajectory in the cartesian space

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

#include "sun_traj_lib/Line_Segment_Traj.h"

using namespace TooN;
using namespace std;

namespace sun
{
/*======CONSTRUCTORS========*/

/*
    Full Constructor
*/
Line_Segment_Traj::Line_Segment_Traj(const Vector<3> &pi, const Vector<3> &pf, const Scalar_Traj_Interface &traj_s)
  : Position_Traj_Interface(NAN, NAN), _pi(pi), _pf(pf), _traj_s(traj_s.clone())
{
}

/*
    Copy Constructor
*/
Line_Segment_Traj::Line_Segment_Traj(const Line_Segment_Traj &traj)
  : Position_Traj_Interface(traj), _pi(traj._pi), _pf(traj._pf), _traj_s(traj._traj_s->clone())
{
}

/*
    Clone the object in the heap
*/
Line_Segment_Traj *Line_Segment_Traj::clone() const
{
  return new Line_Segment_Traj(*this);
}

/*======END CONSTRUCTORS========*/

/*====== GETTERS ========*/

/*
    Get direction of the Line Segment as unit vector
*/
Vector<3> Line_Segment_Traj::getDirection() const
{
  Vector<3> dir = _pf - _pi;
  return (dir / norm(dir));
}

/*
    Get length of the segment
*/
double Line_Segment_Traj::getLength() const
{
  return norm(_pf - _pi);
}

/*
    TODO
*/
Vector<3> Line_Segment_Traj::getInitialPoint() const
{
  return _pi;
}

/*
    TODO
*/
Vector<3> Line_Segment_Traj::getFinalPoint() const
{
  return _pf;
}

/*
    Get the final time instant
*/
double Line_Segment_Traj::getFinalTime() const
{
  return _traj_s->getFinalTime();
}

/*
    Get the initial time instant
*/
double Line_Segment_Traj::getInitialTime() const
{
  return _traj_s->getInitialTime();
}

/*====== END GETTERS ========*/

/*====== SETTERS =========*/

/*
    Set the scalar trajectory
    Trajectory for the scalar s variable should be a traj from 0 to 1
    s = 0 -> _pi   &   s = 1 -> _pf
    Note: Velocities and accelerations
    Since the s is normalized using getLength() also the ds and dds have to be
   normalized
    e.g. _vi = dsi / line_segment_traj.getLength() where line_segment_traj is
   this object
*/
void Line_Segment_Traj::setScalarTraj(const Scalar_Traj_Interface &s_traj)
{
  _traj_s = Scalar_Traj_Interface_Ptr(s_traj.clone());
}

/*
    TODO
*/
void Line_Segment_Traj::setInitialPoint(Vector<3> pi)
{
  _pi = pi;
}

/*
    TODO
*/
void Line_Segment_Traj::setFinalPoint(Vector<3> pf)
{
  _pf = pf;
}

/*
    Change the initial time instant (translate the trajectory in the time)
*/
void Line_Segment_Traj::changeInitialTime(double initial_time)
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
void Line_Segment_Traj::changeFrame(const Matrix<4, 4> &new_T_curr)
{
  Vector<4> tmp_v;
  tmp_v[3] = 1.0;

  tmp_v.slice<0, 3>() = _pi;
  _pi = (new_T_curr * tmp_v).slice<0, 3>();

  tmp_v.slice<0, 3>() = _pf;
  _pf = (new_T_curr * tmp_v).slice<0, 3>();
}

/*====== END TRANSFORM =========*/

/*====== RUNNERS =========*/

/*
    Get Position at time secs
*/
Vector<3> Line_Segment_Traj::getPosition(double secs) const
{
  return _pi + (_traj_s->getPosition(secs) * (_pf - _pi));
}

/*
    Get Velocity at time secs
*/
Vector<3> Line_Segment_Traj::getVelocity(double secs) const
{
  return _traj_s->getVelocity(secs) * (_pf - _pi);
}

/*
    Get Acceleration at time secs
*/
Vector<3> Line_Segment_Traj::getAcceleration(double secs) const
{
  return _traj_s->getAcceleration(secs) * (_pf - _pi);
}

/*====== END RUNNERS =========*/

}  // namespace sun